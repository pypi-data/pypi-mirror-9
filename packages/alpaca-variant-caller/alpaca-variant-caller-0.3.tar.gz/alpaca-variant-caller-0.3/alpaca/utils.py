
"""
Common utility functions.
"""

__author__ = "Johannes Köster"
__license__ = "MIT"


import math
import logging
from distutils.version import StrictVersion
import fcntl
import contextlib
from contextlib import contextmanager

import numpy as np
import h5py
from scipy.misc import comb
from pyopencl import array as cl_array
import pyopencl as cl
from pyopencl.elementwise import ElementwiseKernel
from pyopencl.scan import InclusiveScanKernel
from pyopencl.tools import MemoryPool, ImmediateAllocator
from pytools import memoize_method
from mako.template import Template


MIN_FLOAT = np.finfo(np.float32).min
MAX_INT = np.iinfo(np.int32).max
LOG_TO_PHRED_FACTOR = np.float32(-10 * 1 / math.log(10))
PHRED_TO_LOG_FACTOR = np.float32(1 / (-10 * math.log10(math.e)))


CL_DEVICE_TYPES = {
    "gpu": cl.device_type.GPU,
    "cpu": cl.device_type.CPU,
    "accelerator": cl.device_type.ACCELERATOR,
    "any": cl.device_type.ALL
}


def cl_logsum(double=False):
    """The following method is from the script
    Algorithmische Bioinformatik of Sven Rahmann (2013).
    """
    return Template(r"""
        inline float logsum(${dt} a, ${dt} b)
        {
            const float max_prob = max(a, b);
            return max_prob + log1p(exp(a - max_prob) + exp(b - max_prob) - 1);
            /*if(b > a) {
                const ${dt} t = a;
                a = b;
                b = t;
            }
            return a + log1p(exp(b - a));*/
        }
        """).render(dt="double" if double else "float")


def cl_logsum_array(count=2, double=False):
    return Template(
        r"""
        inline ${dt} logsum_array(${dt}* log_probs)
        {
            // find maximum probability
            ${dt} max_prob = log_probs[0];
            #pragma unroll
            for(int i=1; i<${count}; i++)
                max_prob = max(max_prob, log_probs[i]);

            // sum up log prob minus maximum log prob
            // since the maximum prob should be excluded from the sum
            // we start with -1 (since exp(log p_0 - log p_0) = 1 if p_0 maximum)
            ${dt} prob_sum = -1;
            #pragma unroll
            for(int i=0; i<${count}; i++)
                prob_sum += exp(log_probs[i] - max_prob);

            return max_prob + log1p(prob_sum);
        }
        """
    ).render(count=count, dt="double" if double else "float")


def cl_log_cumsum(context, dtype):
    return InclusiveScanKernel(
        context,
        dtype,
        "logsum(a, b)",
        neutral=str(MIN_FLOAT),
        name_prefix="logcumsum",
        preamble=cl_logsum()
    )


np_slice = np.s_


def np_round_to_int(array):
    return np.asarray(np.round(np.minimum(array, MAX_INT)), dtype=np.int32)


def np_index_true(array):
    return np.asarray(np.nonzero(array)[0], dtype=np.int32)


def comb_with_repl(n, k):
    return comb(n + k - 1, k, exact=True)


def is_higher_version(a, b):
    return StrictVersion(a) > StrictVersion(b)


def init_opencl(device_type="cpu", threads=None):
    def get_subdevice(device, threads):
        subdev = None
        try:
            subdev = device.create_sub_devices(
                [cl.device_partition_property.EQUALLY, threads]
            )[0]
        except AttributeError:
            subdev = device.create_sub_devices_ext(
                [cl.device_partition_property_ext.EQUALLY, threads]
            )[0]
        return subdev

    if device_type != "cpu":
        threads = None
    cl_device_type = CL_DEVICE_TYPES[device_type]

    for platform in cl.get_platforms():
        devices = platform.get_devices(device_type=cl_device_type)
        if not devices:
            continue
        device = devices[0]
        cores = device.get_info(cl.device_info.MAX_COMPUTE_UNITS)
        if threads is not None and threads < cores:
            subdevice = get_subdevice(device, threads)
            if subdevice is None:
                logging.warning(
                    "OpenCL device does not support creating sub-devices. "
                    "Used cores may exceed given thread count."
                )
            else:
                device = subdevice

        cl_ctx = cl.Context([device])
        cl_queue = cl.CommandQueue(cl_ctx)

        # TODO mem_flags cause error
        # invalid value - cannot specify USE_HOST_PTR or COPY_HOST_PTR flags
        mem_flags = cl.mem_flags.READ_WRITE
        if device_type == "cpu":
            mem_flags |= cl.mem_flags.USE_HOST_PTR

        cl_mem_pool = MemoryPool(ImmediateAllocator(cl_queue))
        return cl_queue, cl_mem_pool
    raise AlpacaError(
        "No OpenCL driver for {} installed. "
        "Please install an SDK or appropriate driver.".format(device_type))


class CLAlgorithm:
    def __init__(self, cl_queue, cl_mem_pool):
        self.cl_queue = cl_queue
        self.cl_mem_pool = cl_mem_pool

    def to_device(self, ary, async=False):
        return cl_array.to_device(
            self.cl_queue, ary, allocator=self.cl_mem_pool, async=async
        )

    def empty(self, shape, dtype):
        return cl_array.empty(
            self.cl_queue, shape, dtype, allocator=self.cl_mem_pool
        )

    def empty_like(self, ary):
        return cl_array.empty_like(ary)

    def zeros(self, shape, dtype):
        return cl_array.zeros(
            self.cl_queue, shape, dtype, allocator=self.cl_mem_pool
        )

    def zeros_like(self, ary):
        return cl_array.zeros_like(ary)

    def arange(self, *args, **kwargs):
        return cl_array.arange(*args, allocator=self.cl_mem_pool, **kwargs)

    def get_dimensions(self, global_shape, work_group_size):
        assert len(global_shape) == 1 # the rest is not implemented yet
        global_size = global_shape[0]
        return (
            [work_group_size * math.ceil(global_size / work_group_size)],
            [work_group_size]
        )


class AlpacaError(Exception):
    pass


def lazy_property(func):
    attr_name = "_lazy_" + func.__name__

    @property
    def f(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return f


def bufferable_property(func):
    attr_name = "_buffer_" + func.__name__

    def f(self, buffer=False):
        if not hasattr(self, attr_name):
            value = func(self)
            if buffer:
                setattr(self, attr_name, value)
            return value
        return getattr(self, attr_name)

    return f


@contextmanager
def flocked(path):
    """ Locks FD before entering the context, always releasing the lock. """
    with open(path, "br") as fd:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)


def print_progress(processed, reference_length, megabase=1000 ** 2):
    logging.info(
        "{:,.2f} of {:,.2f} megabases ({:.2%}) processed".format(
            processed / megabase,
            reference_length / megabase,
            processed / reference_length
        )
    )


def mergesorted(a, b):
    """Return indices such that sorted arrays a and b can be merged into sorted target array."""
    if not a.size or not b.size:
        return np.arange(a.size), np.arange(b.size)

    # find positions of b inside a
    idx = np.searchsorted(a, b)
    # shift insertion positions of b elements at same sites
    b_dest = idx + np.arange(b.size)

    # determine shift of a elements behind inserts from b
    a_dest = np.bincount(idx, minlength=a.size)[:a.size]
    # sum up shifts
    a_dest = np.cumsum(a_dest)
    # shift elements being inserted at the same position
    a_dest += np.arange(a_dest.size)

    return a_dest, b_dest
