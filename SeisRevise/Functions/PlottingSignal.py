import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def drawing_signal(left_edge, frequency, signal, label, output_folder,
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
    :param output_name: имя файла рисунка графика
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
    plt.savefig(output_folder + '/' + output_name + '.png', dpi=96)

    # закрытие плота
    plt.close(fig)
