import numpy as np


def cross_correlation(frequency, f_min_analysis, f_max_analysis, amplitudes):
    """
    Функция для вычисления коэффициентов корреляции между столбцами массивов
    амплитуд спектров
    :param frequency: одномерный массив numpy с набором частот
    :param f_min_analysis: минимальная частота для расчета коэф-та корреляции
    :param f_max_analysis: максимальная частота для расчета коэф-та корреляции
    :param amplitudes: матрица только со значения амплитуд различных спектров,
        в каждой строке данные одного спектра
    :return: матрица с рассчитанными значениями корреляции
    всех спектров со всеми
    В результате получается зеркальная матрица значений с единичной диагональю
    """
    # выборка амплитуд в пределах указанных частот
    selection_amplitudes = amplitudes[(f_min_analysis <= frequency) *
                                      (frequency <= f_max_analysis)]

    # создание пустой матрицы для сохранения в нее коэф-тов корреляции
    correlation_matrix = np.empty((amplitudes.shape[1], amplitudes.shape[1]),
                                  dtype=np.float32)

    # вычисление и заполнение коэф-тов корреляции
    for i in range(amplitudes.shape[1]):
        for j in range(amplitudes.shape[1]):
            correlation = np.corrcoef(selection_amplitudes[:, i],
                                      selection_amplitudes[:, j])[0, 1]
            correlation_matrix[i, j] = correlation

    # возврат результатов
    return correlation_matrix
