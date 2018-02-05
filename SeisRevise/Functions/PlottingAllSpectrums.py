import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def drawing_all_smooth_cumulative_spectrums(spectrums_name_list,
                                            frequency,
                                            spectrum_data,
                                            f_min_visualize,
                                            f_max_visualize,
                                            colors,
                                            output_folder,
                                            output_name):
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
    :param output_name: имя выходного png-файла
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
        spectrum_data[(frequency >= f_min_visualize) * (frequency <= f_max_visualize)]

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
    plt.savefig(output_folder + '/' + output_name + '.png', dpi=200)
    # закрытие плота
    plt.close(fig)
