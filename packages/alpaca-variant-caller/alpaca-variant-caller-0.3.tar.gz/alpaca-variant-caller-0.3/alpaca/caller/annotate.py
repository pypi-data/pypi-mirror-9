
import logging

import numpy as np
import pyopencl.clmath as clmath
import pyopencl.array as clarray
import pyopencl.clmath as clmath
from pyopencl.scan import InclusiveScanKernel
from pyopencl.elementwise import ElementwiseKernel
import scipy.stats

from alpaca.utils import CLAlgorithm, PHRED_TO_LOG_FACTOR, LOG_TO_PHRED_FACTOR, MIN_FLOAT, np_round_to_int, cl_log_cumsum


class FDR(CLAlgorithm):
    def __init__(self, cl_queue, cl_mem_pool):
        super().__init__(cl_queue, cl_mem_pool)
        self.cl_calc_log_cumsum = cl_log_cumsum(cl_queue.context, np.float32)

    def calc_max_prob(self, calls, fdr):
        assert calls
        quals = np.sort(np.concatenate([c.quals for c in calls]))
        cl_quals = self.to_device(quals)

        cl_expected_fdr = self.cl_calc_log_cumsum(cl_quals)
        expected_fdr = clmath.exp(cl_expected_fdr).get()

        i = max(
            0,
            min(
                np.searchsorted(expected_fdr, fdr, side="right") - 1,
                len(quals) - 1
            )
        )
        return quals[i], expected_fdr[i]


def adjust_quals(cl_queue, cl_mem_pool, all_calls, multiple_testing_count):
    bonferroni_holm = BonferroniHolm(cl_queue, cl_mem_pool)

    if all_calls:
        quals = np.concatenate([calls.quals for calls in all_calls])
        adjusted_quals = bonferroni_holm.adjust(quals, multiple_testing_count)

        i = 0
        for calls in all_calls:
            calls.adjusted_quals = adjusted_quals[i:i + len(calls)]
            i += len(calls)
    return all_calls


class BonferroniHolm(CLAlgorithm):

    def __init__(self, cl_queue, cl_mem_pool):
        super().__init__(cl_queue, cl_mem_pool)

        self.cl_adjust_qual = InclusiveScanKernel(self.cl_queue.context, np.float32, "max(a, b)", neutral=str(MIN_FLOAT), name_prefix="adjust_qual")

        self.cl_multiply_factor = ElementwiseKernel(cl_queue.context,
        "const int test_count, "
        "float* quals",
        """
        const float factor = log((float)test_count - i);
        quals[i] = min(quals[i] + factor, 0.0f);
        """)

    def adjust(self, quals, multiple_testing_count):
        """ Corrects quals according to Bonferroni-Holm method. """

        sort = np.argsort(quals)
        unsort = np.argsort(sort)
        cl_quals = self.to_device(quals[sort])

        self.cl_multiply_factor(multiple_testing_count, cl_quals)
        self.cl_adjust_qual(cl_quals)

        return cl_quals.get()[unsort]
