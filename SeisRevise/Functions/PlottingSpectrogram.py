import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

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

    # размер поля для вывода графика
    mpl.rcParams['figure.figsize'] = (12, 9)
    mpl.rcParams['figure.dpi'] = 96  # разрешение отображения графика
    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')
    plt.subplot(111)  # подготовка плота
    # отображение спектрограммы в виде децибелов=20*lg(|amp|)
    plt.pcolormesh(times, frequencies, 20 * np.log10(abs(amplitudes)),
                   cmap=cmap, norm=cnorm)
    # заголовки осей
    x_label = u'Время, с'
    y_label = u'Частота, Гц'
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    # подпись графика
    plt.title(output_name, fontsize=10)

    # сохранение графика в png
    plt.savefig(output_folder + '/' + output_name + '.png', dpi=96)

    # очистка плота для построения нового графика
    plt.gcf().clear()
