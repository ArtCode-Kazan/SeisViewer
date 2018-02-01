import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from SeisCore import specgram
from SeisCore.MSICore.DrawingFunctions.Spectrogram import scale


def plot_spectrogram(signal, frequency, window_size,
                     noverlap_size, min_frequency_visulize,
                     max_frequency_visualize, output_folder,
                     output_name, time_start_sec=0):

    # расчет спектрограммы
    times, frequencies, amplitudes = specgram(
        time_start=time_start_sec,
        signal_data=signal,
        frequency_of_signal=frequency,
        nfft_window_size=window_size,
        noverlap_size=noverlap_size,
        min_frequency=min_frequency_visulize,
        max_frequency=max_frequency_visualize
    )

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
    fig.set_size_inches(12,9)
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
    plt.savefig(output_folder + '/' + output_name + '.png', dpi=96)

    # закрытие плота
    plt.close()
