import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def drawing_correlation(devices, colors,correlation_matrix,
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
    plt.savefig(output_folder + '/' + output_name + '.png', dpi=200)
    # закрытие плота
    plt.close(fig)
