import math
from collections import namedtuple

import numpy as np

from alpaca.index.utils import calc_genotype_allelefreq_probability, calc_genotypes, BITENCODE_TRANSLATION_TABLE
from alpaca.utils import PHRED_TO_LOG_FACTOR

########## Bayesian calling ############

prob_dtype = np.float64
Pileup = namedtuple("Pileup", "bases quals")
Priors = namedtuple("Priors", "ploidy heterozygosity ref_base genotypes genotype_af_probs")


class Pileup:
    def __init__(self, bases, quals):
        self.bases = np.frombuffer(bases.translate(BITENCODE_TRANSLATION_TABLE), dtype=np.int8)
        self.quals = np.frombuffer(quals, dtype=np.int8)
        self.quals = np.asarray(self.quals, dtype=prob_dtype) - 33
        self.quals *= PHRED_TO_LOG_FACTOR


confusion_matrix = np.log(
    np.array(
        [
            [1, 0.58, 0.17, 0.25],
            [0.35, 1, 0.11, 0.54],
            [0.32, 0.05, 1, 0.63],
            [0.46, 0.22, 0.32, 1]
        ],
        dtype=prob_dtype
    )
)


def logsum(probs):
    max_prob = probs.max()
    if max_prob == -np.inf:
        return -np.inf
    probs = probs - max_prob
    probs = np.exp(probs)
    res = max_prob + np.log1p(probs.sum() - 1)
    return res


def column_logsum(probs):
    probs = probs.copy()
    max_probs = probs.max(axis=0)
    for i in range(probs.shape[0]):
        probs[i] -= max_probs
    probs = np.exp(probs)
    res = max_probs + np.log1p(probs.sum(axis=0) - 1)
    return res


def allele_likelihoods(pileup, allele):
    likelihoods = np.empty_like(pileup.quals)
    matches = pileup.bases == allele
    subst = np.logical_not(matches)

    likelihoods[matches] = np.log1p(-np.exp(pileup.quals[matches]))
    likelihoods[subst] = pileup.quals[subst] + confusion_matrix[allele, pileup.bases[subst]]
    return likelihoods


def genotype_likelihood(pileup, genotype):
    ploidy = len(genotype)
    lhs = np.array(
        [
            allele_likelihoods(pileup, allele)
            for allele in genotype
        ], dtype=pileup.quals.dtype
    )
    lhs = column_logsum(lhs)
    lhs -= np.log(ploidy)
    assert np.all(lhs <= 0)
    res = lhs.sum()
    return res


def allele_frequency_likelihood(pileup, allele_frequency, priors):
    prior = priors.genotype_af_probs[allele_frequency]
    lhs = np.array(
        [
            genotype_likelihood(pileup, genotype)
            for genotype in priors.genotypes
            if (genotype != priors.ref_base).sum() == allele_frequency
        ]
    )
    lhs += prior
    likelihood = logsum(lhs)
    return likelihood


def total_allele_frequency_likelihood(pileups, allele_frequency, priors):
    return np.sum([
        allele_frequency_likelihood(
            pileup,
            allele_frequency,
            priors
        )
        for pileup in pileups
    ])


def allele_frequency_priors(pileups, ploidy, heterozygosity):
    sample_count = len(pileups)
    max_allele_freq = sample_count * ploidy
    allelefreq_priors = np.arange(max_allele_freq + 1, dtype=pileups[0].quals.dtype)
    allelefreq_priors[1:] = np.log(heterozygosity) - np.log(allelefreq_priors[1:])

    allelefreq_priors[0] = np.log(
        1 - heterozygosity *
        sum(
            1 / i
            for i in range(
                1, max_allele_freq + 1
            )
        )
    )
    return allelefreq_priors


def sample_allele_frequency_likelihoods(pileups, priors):
    return np.array([
        [
            allele_frequency_likelihood(pileup, af, priors)
            for af in range(priors.ploidy + 1)
        ]
        for pileup in pileups
    ])


def marginal_pileup_probability(pileups, priors, af_priors):
    sample_count = len(pileups)
    max_allele_freq = sample_count * priors.ploidy

    sample_af_likelihoods = sample_allele_frequency_likelihoods(pileups, priors)
    print(np.exp(sample_af_likelihoods))

    z = np.empty((sample_count + 1, max_allele_freq + 1), dtype=prob_dtype)
    z[:, :] = -np.inf
    z[0, 0] = 0

    for k in range(max_allele_freq + 1):
        for j in range(1, sample_count + 1):
            ks = [
                k_ for k_ in range(priors.ploidy + 1)
                if k-k_ >= 0 and k-k_ <= max_allele_freq
            ]
            summands = [
                z[j-1, k-k_] + sample_af_likelihoods[j-1, k_]
                for k_ in ks
            ]
            z[j, k] = logsum(
                np.array(
                    summands, dtype=prob_dtype
                )
            )
            print("z", np.exp(z))

    af_probs = z[sample_count, :] + af_priors
    prob =  logsum(af_probs)
    print(np.exp(prob))
    return prob


def calc_priors(ref_base=b"A", ploidy=2, heterozygosity=0.001):
    ref_base = ord(b"A".translate(BITENCODE_TRANSLATION_TABLE))
    genotype_af_probs = calc_genotype_allelefreq_probability(ploidy)
    genotypes = calc_genotypes(ploidy)
    return Priors(ploidy, heterozygosity, ref_base, genotypes, genotype_af_probs)


def reference_genotype_probability(pileups, ref_base=b"A", ploidy=2, heterozygosity=0.001):
    priors = calc_priors(ref_base, ploidy, heterozygosity)
    af_priors = allele_frequency_priors(pileups, ploidy, heterozygosity)

    prior = af_priors[0]
    likelihood = total_allele_frequency_likelihood(pileups, 0, priors)
    marginal = marginal_pileup_probability(pileups, priors, af_priors)

    assert prior <= 0 and likelihood <= 0 and marginal <= 0
    # float32 precision can cause values of 0 + eps here.
    # these are irrelevant, since they are no-calls, so we set them to 0
    return min(prior + likelihood - marginal, 0)


def difference(prob_a, prob_b):
    return np.log1p(-np.exp(np.log1p(-np.exp(prob_a)) + prob_b))


def union(prob_a, prob_b):
    return prob_a + prob_b


def relaxed_intersection(pileups, min_variant, ref_base=b"A", ploidy=2, heterozygosity=0.001):
    priors = calc_priors(ref_base, ploidy, heterozygosity)
    af_priors = allele_frequency_priors(pileups, ploidy, heterozygosity)

    # calculate the probability for at least <min_variant> non-ref samples with dynamic programming
    sample_count = len(pileups)

    assert min_variant >= 0 and min_variant <= sample_count

    sample_reference_genotype_probabilities = np.array(
        [
            reference_genotype_probability([pileup], ref_base, ploidy, heterozygosity)
            for pileup in pileups
        ],
        dtype=prob_dtype
    )

    z = np.empty((sample_count + 1, min_variant + 1), dtype=prob_dtype)
    z[:, :] = -np.inf
    z[0,0] = 0

    # k is the number of variant samples
    # j indicates the subset 1,...,j of samples investigated
    for k in range(min_variant + 1):
        for j in range(1, sample_count + 1):
            summands = np.array(
                [
                    z[j-1, k-1] + np.log1p(-np.exp(sample_reference_genotype_probabilities[j-1])),
                    z[j-1, k] + sample_reference_genotype_probabilities[j-1]
                ],
                dtype=prob_dtype
            )
            z[j,k] = logsum(summands)
    # the probability for less than <min_variant> non-ref samples is 
    # the sum over 0 <= k < min_variant
    return logsum(z[sample_count, :min_variant])


if __name__ == "__main__":
    pileups = [
        Pileup(b"AACC" * 10, b"IIII" * 10),
        Pileup(b"AAAA" * 10, b"IIII" * 10),
    ]
    print(reference_genotype_probability(pileups))
    #print(relaxed_intersection(pileups, 1))
