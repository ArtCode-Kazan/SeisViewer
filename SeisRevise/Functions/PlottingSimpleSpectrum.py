from scipy.signal import medfilt
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from SeisCore.GeneralCalcFunctions.Spectrum import spectrum
from SeisCore.GeneralCalcFunctions.MarmettFilter import marmett


def simple_spectrum(signal, frequency, median_filter_parameter,
                    marmett_filter_parameter, f_min, f_max,
                    output_folder, output_name):
    """
    Функция для построения простого спектра Фурье и спектра Фурье со
    скглаживанием
    :param signal: исходный сигнал (одномерный массив numpy)
    :param frequency: частота сигнала
    :param median_filter_parameter: параметр медианного фильтра
    :param marmett_filter_parameter: парметр фильтра marmett
    :param f_min: минимальная частота визуализации
    :param f_max: максимальная частота визуализации
    :param output_folder: папка сохранения результатов
    :param output_name: имя выходного файла
    :return: void
    """
    # расчет спектра сигнала
    spectrum_data = spectrum(signal=signal, frequency=frequency)

    freqs = spectrum_data[:, 0]         # частотный ряд
    amplitudes = spectrum_data[:, 1]    # амплитудный ряд

    # проведение фильтрации спектра
    filtered_amplitudes = amplitudes
    if median_filter_parameter is not None:
        filtered_amplitudes = medfilt(filtered_amplitudes,
                                      median_filter_parameter)
    if marmett_filter_parameter is not None:
        filtered_amplitudes = marmett(signal=filtered_amplitudes,
                                      order=marmett_filter_parameter)

    # получение среза частот в заданном частотном диапазоне визуализации
    selection_frequency = freqs[(freqs >= f_min) * (freqs <= f_max)]

    # получение срезов массивов амплитуд в заданном частотном диаппазоне
    selection_spectrum_begin_amplitudes = \
        amplitudes[(freqs >= f_min) * (freqs <= f_max)]

    selection_spectrum_smooth_amplitudes = \
        filtered_amplitudes[(freqs >= f_min) * (freqs <= f_max)]

    # поиск максимальной и минимальной амплитуды в выборках
    amp_min = np.min([np.min(selection_spectrum_begin_amplitudes),
                      np.min(selection_spectrum_smooth_amplitudes)])
    amp_max = np.max([np.max(selection_spectrum_begin_amplitudes),
                      np.max(selection_spectrum_smooth_amplitudes)])

    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')

    # настройка отступов полей
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.8
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    # создание бланка графика
    fig = plt.figure()

    # размер плота в дюймах
    fig.set_size_inches(13, 10)
    # разрешение отображения графика
    fig.dpi = 96
    # подготовка осей
    axes = fig.add_subplot(111)

    # пределы по осям
    axes.set_xlim(f_min, f_max)
    axes.set_ylim(amp_min, amp_max)

    # построение графика исходного, несглаженного спектра (толщина линии 1)
    axes.plot(selection_frequency, selection_spectrum_begin_amplitudes,
              lw=1, color='#000000',
              label=u'Спектр Фурье\n(без сглаживания))')

    axes.plot(selection_frequency, selection_spectrum_smooth_amplitudes,
              lw=2, color='#FF0000',
              label=u'Спектр Фурье\n(со сглаживанием)')

    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # заголовки осей
    x_label = u'Частота, Гц'
    y_label = u'Амплитуда, усл. ед'
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)
    # подпись графика
    axes.set_title(output_name, fontsize=10)

    axes.grid()  # включение сетки графика

    # сохранение графика в png
    plt.savefig(output_folder + '/' + output_name + '.png', dpi=96)

    # закрытие плота
    plt.close(fig)
