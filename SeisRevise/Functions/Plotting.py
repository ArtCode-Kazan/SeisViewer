import os

import numpy as np
from scipy.signal import medfilt
import matplotlib as mpl
import matplotlib.pyplot as plt

from SeisCore.GeneralCalcFunctions.Spectrogram import specgram
from SeisCore.GeneralPlottingFunctions.Spectrogram import scale
from SeisCore.GeneralCalcFunctions.Spectrum import spectrum
from SeisCore.GeneralCalcFunctions.MarmettFilter import marmett


def plot_spectrogram(signal, frequency, window_size,
                     noverlap_size, min_frequency_visulize,
                     max_frequency_visualize, output_folder,
                     output_name, time_start_sec=0):
    """
    Функция для построения 2D спектрограммы в виде картинки
    :param signal: входной сигнал numpy (1D массив)
    :param frequency: частота сигнала, Гц
    :param window_size: размер окна расчета, отсчеты
    :param noverlap_size: размер сдвига окна, отсчеты
    :param min_frequency_visulize: минимальная частота для визуализации
    :param max_frequency_visualize: максимальная частота для визуализации
    :param output_folder: папка для экспорта рисунка
    :param output_name: имя файла рисунка (без расширения!)
    :param time_start_sec: время начала куска сигнала (в секундах)
    :return: True, если функция успешно завершена, False, если произошли
    ошибки
    """
    # расчет спектрограммы проба расчета, в случае ошибки функция вернет False
    try:
        times, frequencies, amplitudes = specgram(
            time_start=time_start_sec,
            signal_data=signal,
            frequency_of_signal=frequency,
            nfft_window_size=window_size,
            noverlap_size=noverlap_size,
            min_frequency=min_frequency_visulize,
            max_frequency=max_frequency_visualize)
    except ValueError:
        return False

    # расчет параметров шкалы
    cmap, cnorm = scale(amplitudes)

    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')

    # настройка отступов полей
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    # создание бланка графика
    fig = plt.figure()

    # размер плота в дюймах
    fig.set_size_inches(12, 9)
    # разрешение отображения графика
    fig.dpi = 96
    # подготовка осей
    axes = fig.add_subplot(111)

    # отображение спектрограммы в виде децибелов=20*lg(|amp|)
    axes.pcolormesh(times, frequencies, 20 * np.log10(abs(amplitudes)),
                    cmap=cmap, norm=cnorm)
    # заголовки осей
    x_label = u'Время, с'
    y_label = u'Частота, Гц'
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)

    # подпись графика
    axes.set_title(output_name, fontsize=10)
    # сохранение графика в png
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)
    # закрытие плота
    plt.close()

    # проверка, что файл спектрограммы создан
    if os.path.exists(export_path):
        return True
    else:
        return False


def plot_signal(left_edge, frequency, signal, label, output_folder,
                output_name):
    """
    Функция для построения графика сигнала
    :param left_edge: номер отсчета, с которого строится сигнал (нужен для
    построения временного ряда)
    :param frequency: частота дискретизации (нужен для построения временного ъ
    ряда)
    :param signal: одномерный массив сигнала
    :param label: заголовок графика
    :param output_folder: папка куда сохраняется график
    :param output_name: имя файла рисунка графика (без расширения)
    :return: None
    """
    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')

    # настройка отступов полей
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
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
    # ось x - время в секундах
    t_min = left_edge / frequency
    t_max = (left_edge + signal.shape[0] - 1) / frequency
    axes.set_xlim(t_min, t_max)
    # ось y - амплитуда сигнала
    amp_min = np.min(signal)
    amp_max = np.max(signal)
    axes.set_ylim(amp_min, amp_max)

    # генерация массива времен
    time_array = np.linspace(start=t_min, stop=t_max, num=signal.shape[0])

    # построение графика
    axes.plot(time_array, signal, lw=0.5, color='#FF0000')

    # заголовки осей
    x_label = u'Время, с'
    y_label = u'Амплитуда, усл. ед'
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)
    # подпись графика
    axes.set_title(label, fontsize=10)

    plt.grid()  # включение сетки графика

    # сохранение графика в png
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)

    # закрытие плота
    plt.close(fig)


def plot_simple_spectrum(signal, frequency, median_filter_parameter,
                         marmett_filter_parameter, f_min, f_max,
                         output_folder, output_name):
    """
    Функция для построения простого спектра Фурье и спектра Фурье со
    сглаживанием
    :param signal: исходный сигнал (одномерный массив numpy)
    :param frequency: частота сигнала
    :param median_filter_parameter: параметр медианного фильтра
    :param marmett_filter_parameter: параметр фильтра marmett
    :param f_min: минимальная частота визуализации
    :param f_max: максимальная частота визуализации
    :param output_folder: папка сохранения результатов
    :param output_name: имя выходного файла
    :return: void
    """
    # расчет спектра сигнала
    spectrum_data = spectrum(signal=signal, frequency=frequency)

    freqs = spectrum_data[:, 0]  # частотный ряд
    amplitudes = spectrum_data[:, 1]  # амплитудный ряд

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

    # получение срезов массивов амплитуд в заданном частотном диапазоне
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
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)

    # закрытие плота
    plt.close(fig)


def plot_average_spectrum(frequency, spectrum_begin_amplitudes,
                          spectrum_smooth_amplitudes,
                          f_min, f_max,
                          output_folder, output_name):
    """
    Функция для оформления осредненного (кумулятивного) спектра в виде
    png-картинки, на которой отображается исходный средний спектр (без
    сглаживания) и средний спектр с параметрами сглаживания (медианный
    фильтр и (или) фильтр Marmett)
    :param frequency: общий ряд частот как для спектра без сглаживания,
    так и со сглаживанием
    :param spectrum_begin_amplitudes: набор амплитуд изначального среднего
    спектра без сглаживания
    :param spectrum_smooth_amplitudes: набор амплитуд среднего спектра
    после сглаживания
    :param f_min: минимальная частота отображения спектра.
    Может быть None - по умолчанию миниальная частота спектра
    :param f_max: максимальная частота отображения спектра
    Может быть None - по умолчанию максимальная частота спектра
    :param output_folder: выходная папка сохранения спектра
    :param output_name: выходное имя файла картинки спектра
    :return: функция ничего не возвращает. Работает как процедура
    """
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
    if f_min is None:
        f_min = frequency[0]
    if f_max is None:
        f_max = frequency[-1]
    axes.set_xlim(f_min, f_max)

    # получение среза частот в заданном частотном диапазоне визуализации
    selection_frequency = frequency[
        (frequency >= f_min) * (frequency <= f_max)]

    # получение срезов массивов амплитуд в заданном частотном диаппазоне
    selection_spectrum_begin_amplitudes = \
        spectrum_begin_amplitudes[(frequency >= f_min) * (frequency <= f_max)]

    selection_spectrum_smooth_amplitudes = \
        spectrum_smooth_amplitudes[(frequency >= f_min) * (frequency <= f_max)]

    # поиск максимальной и минимальной амплитуды в выборках
    amp_min = np.min([np.min(selection_spectrum_begin_amplitudes),
                      np.min(selection_spectrum_smooth_amplitudes)])
    amp_max = np.max([np.max(selection_spectrum_begin_amplitudes),
                      np.max(selection_spectrum_smooth_amplitudes)])
    axes.set_ylim(amp_min, amp_max)

    # построение графика исходного, несглаженного спектра (толщина линии 1)
    axes.plot(selection_frequency, selection_spectrum_begin_amplitudes,
              lw=1, color='#000000',
              label=u'Кумулятивный спектр\n(без сглаживания))')

    axes.plot(selection_frequency, selection_spectrum_smooth_amplitudes,
              lw=2, color='#FF0000',
              label=u'Кумулятивный спектр\n(со сглаживанием)')

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
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)

    # закрытие плота
    plt.close(fig)


def plot_all_smooth_spectrums(spectrums_name_list, frequency, spectrum_data,
                              f_min_visualize, f_max_visualize, colors,
                              output_folder, output_name):
    """
    Функция для построения плота со всеми сглаженными спектрами всех файлов
    :param spectrums_name_list: названия кривых спектров для легенды
    :param frequency: набор частот спектров
    :param spectrum_data: входной двухмерный массив numpy, в котором каждый
    столбец соответсвует спектру одной кривой, а каждая строка - частоте из
    ряда frequency
    :param f_min_visualize: минимальная частота для визуализации
    :param f_max_visualize: максимальная частота для визуализации
    :param colors: набор цветов для каждой кривой
    :param output_folder: папка, куда будет сохранен график
    :param output_name: имя выходного png-файла (без расширения)
    :return: функция ничего не возвращает. Работает как процедура
    """
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
    if f_min_visualize is None:
        f_min_visualize = frequency[0]
    if f_max_visualize is None:
        f_max_visualize = frequency[-1]
    axes.set_xlim(f_min_visualize, f_max_visualize)

    # получение среза частот в заданном частотном диапазоне визуализации
    selection_frequency = frequency[
        (frequency >= f_min_visualize) * (frequency <= f_max_visualize)]

    # получение срезов массивов амплитуд в заданном частотном диапазоне
    selection_amplitudes = \
        spectrum_data[
            (frequency >= f_min_visualize) * (frequency <= f_max_visualize)
        ]

    # поиск максимальной и минимальной амплитуды в необходимом интервале частот
    amp_min = np.min(selection_amplitudes)
    amp_max = np.max(selection_amplitudes)
    axes.set_ylim(amp_min, amp_max)

    # построение графиков спектров
    spectors_count = spectrum_data.shape[1]
    for i in range(spectors_count):
        amplitudes = selection_amplitudes[:, i]
        axes.plot(selection_frequency, amplitudes,
                  label=spectrums_name_list[i],
                  color=colors[i], lw=1)

    # заголовки осей
    x_label = u'Частота, Гц'
    y_label = u'Амплитуда, усл. ед'
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    # вставка легенды
    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # подпись графика
    axes.set_title(output_name, fontsize=10)
    axes.grid()

    # сохранение графика в png
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=200)
    # закрытие плота
    plt.close(fig)


def plot_correlation(devices, colors, correlation_matrix,
                     output_folder, output_name):
    """
    Функция для отрисовки графиков корреляции спектров для кадой пары приборов
    :param devices: список с именами приборов для легенды
    :param colors: цвета графиков
    :param correlation_matrix: матрица со значенями коэф-тов корреляции
    :param output_folder: папка, куда будет сохранен график
    :param output_name: имя выходного png-файла
    :return: функция ничего не возвращает. Работает как процедура
    """
    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')

    # настройка отступов полей
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.8
    mpl.rcParams['figure.subplot.bottom'] = 0.15
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
    axes.set_ylim(0, 1)

    # количество графиков
    graph_count = len(devices)

    # специальная подпись по оси x
    x_values = np.arange(1, graph_count + 1, 1)
    x_labels = devices

    # подпись оси x - пары регистратор-сенсор
    axes.set_xticks(x_values)
    axes.set_xticklabels(x_labels, minor=False, rotation=90)

    # построение графиков коэф-тов корреляции
    for i in range(graph_count):
        coeffs = correlation_matrix[i, :]
        axes.plot(x_values, coeffs,
                  label=devices[i],
                  color=colors[i], lw=1)

    # заголовки осей
    x_label = u'Приборы'
    y_label = u'Коэф-т корреляции'
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    # вставка легенды
    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # подпись графика
    axes.grid()

    # сохранение графика в png
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=200)
    # закрытие плота
    plt.close(fig)
