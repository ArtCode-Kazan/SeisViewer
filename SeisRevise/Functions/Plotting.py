import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import random


plt.switch_backend('SVG')


def generate_random_color():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())


def plot_single_correlation(devices, correlation_data, output_folder,
                            output_name):
    """
    Plotting sigle correlation graph for one device
    :param devices: list with bin-file names
    :param correlation_data: correlation data vector
    :param output_folder: export folder
    :param output_name: export name
    :return: None
    """
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.95
    mpl.rcParams['figure.subplot.bottom'] = 0.2
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()

    fig.set_size_inches(13, 10)

    fig.dpi = 96

    axes = fig.add_subplot(111)

    axes.set_ylim(0, 1.1)

    x_values = np.arange(1, len(devices) + 1, 1)
    x_labels = devices

    axes.set_xticks(x_values)
    axes.set_xticklabels(x_labels, minor=False, rotation=90)

    axes.plot(x_values, correlation_data, color='#FF0000', lw=1)

    x_label = 'Devices'
    y_label = 'Correlation coefficient value'
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    axes.set_title(output_name, fontsize=10)
    axes.grid()

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=200)
    plt.close(fig)


def plot_all_smooth_spectrums(spectrums_name_list, frequency, spectrum_data,
                              f_min_visualize, f_max_visualize, colors,
                              output_folder, output_name):
    """
    Plotting all smooth average spectrums on one graph
    :param spectrums_name_list: filenames for graph legend
    :param frequency: vector of frequency of average spectrum
    :param spectrum_data: spectrum matrix: column - device, row - amplitude
    :param f_min_visualize:
    :param f_max_visualize:
    :param colors: colors for curves
    :param output_folder: export folder
    :param output_name: export name
    :return: None
    """
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.8
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()

    fig.set_size_inches(13, 10)

    fig.dpi = 96

    axes = fig.add_subplot(111)

    if f_min_visualize is None:
        f_min_visualize = frequency[0]
    if f_max_visualize is None:
        f_max_visualize = frequency[-1]
    axes.set_xlim(f_min_visualize, f_max_visualize)

    selection_frequency = frequency[
        (frequency >= f_min_visualize) * (frequency <= f_max_visualize)]

    selection_amplitudes = \
        spectrum_data[
            (frequency >= f_min_visualize) * (frequency <= f_max_visualize)
        ]

    amp_min = np.min(selection_amplitudes)
    amp_max = np.max(selection_amplitudes)
    axes.set_ylim(amp_min, amp_max)

    spectors_count = spectrum_data.shape[1]
    for i in range(spectors_count):
        amplitudes = selection_amplitudes[:, i]
        axes.plot(selection_frequency, amplitudes,
                  label=spectrums_name_list[i],
                  color=colors[i], lw=1)

    x_label = 'Frequency, Hz'
    y_label = 'Amplitude'
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    axes.set_title(output_name, fontsize=10)
    axes.grid()

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=200)
    plt.close(fig)


def plot_correlation(devices, colors, correlation_matrix,
                     output_folder, output_name):
    """
    Ploting general graph with all correlationf for devices
    :param devices: list of file names
    :param colors: graph colors
    :param correlation_matrix: correlation matrix
    :param output_folder: export folder
    :param output_name: export name
    :return: None
    """
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.8
    mpl.rcParams['figure.subplot.bottom'] = 0.2
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()

    fig.set_size_inches(13, 10)
    fig.dpi = 96
    axes = fig.add_subplot(111)

    axes.set_ylim(0, 1)

    graph_count = len(devices)

    x_values = np.arange(1, graph_count + 1, 1)
    x_labels = devices

    axes.set_xticks(x_values)
    axes.set_xticklabels(x_labels, minor=False, rotation=90)

    for i in range(graph_count):
        coeffs = correlation_matrix[i, :]
        axes.plot(x_values, coeffs,
                  label=devices[i],
                  color=colors[i], lw=1)

    x_label = 'Devices'
    y_label = 'Correlation coefficient value'
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    axes.grid()

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=200)
    plt.close(fig)
