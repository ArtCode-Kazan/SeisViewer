import numpy as np


def cross_correlation(frequency, f_min_analysis, f_max_analysis, amplitudes):
    """
    Calculating cross-correlation between all devices
    :param frequency: frequency vector
    :param f_min_analysis: minimal frequency for calculating
    :param f_max_analysis: maximal frequency for calculating
    :param amplitudes: amplitudes matrix
    :return: correlation matrix
    """
    selection_amplitudes = amplitudes[(f_min_analysis <= frequency) *
                                      (frequency <= f_max_analysis)]

    correlation_matrix = np.empty((amplitudes.shape[1], amplitudes.shape[1]),
                                  dtype=np.float)

    for i in range(amplitudes.shape[1]):
        for j in range(amplitudes.shape[1]):
            correlation = np.corrcoef(selection_amplitudes[:, i],
                                      selection_amplitudes[:, j])[0, 1]
            correlation_matrix[i, j] = correlation

    return correlation_matrix

