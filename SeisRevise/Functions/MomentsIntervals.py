def moments_intervals(array_length, frequency, step_time=None):
    """
    Функция для расчета номеров индексов отсчетов для разбития на интервалы
    времени
    :param array_length: длина временного ряда в отсчетах
    :param frequency: частота временного ряда, Гц
    :param step_time: шаг разбиения по времени, часы (по умолчанию None -
    значит берется весь временной интервал)
    :return: список вида (левая граница1, правая граница1), ...
    """
    if step_time is not None:
        step_moments = int(step_time * 3600 * frequency)
    else:
        step_moments = array_length

    # количество блоков интервалов времен
    if array_length % step_moments == 0:
        step_count = int(array_length // step_moments)
    else:
        step_count = int(array_length // step_moments) + 1

    result = list()
    for i in range(step_count):
        # левая граница блока
        left_edge = i * step_moments
        # правая граница блока
        right_edge = left_edge + step_moments
        if right_edge > array_length:
            right_edge = array_length
        result.append((left_edge, right_edge))
    return result
