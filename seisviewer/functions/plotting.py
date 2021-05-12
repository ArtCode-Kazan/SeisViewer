import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


plt.switch_backend('SVG')
mpl.rcParams['agg.path.chunksize'] = 10000


def plot_signals(data: np.ndarray, output_folder: str, output_name: str,
                 norm_coeff=1000, components_order=('X', 'Y', 'Z')) -> None:
    """
    :param data: signal data [4 columns: Time, XChannel, YChannel, ZChannel]
    :param output_folder:
    :param output_name:
    :param norm_coeff:
    :param components_order:
    :return:
    """
    fig, axes = plt.subplots(3, 1)
    fig.set_size_inches(20, 18)
    fig.dpi = 96
    for i, component in enumerate(components_order):
        axes[i].plot(data[:, 0], data[:, 1 + i] / norm_coeff, lw=0.5,
                     color='#FF0000')
        axes[i].set_xlim(data[0, 0], data[-1, 0])
        axes[i].set_xlabel('Time, seconds')
        axes[i].set_ylabel(f'Amplitude, c.u x{norm_coeff}')
        if i == 0:
            title = f'{output_name}\nChannel_{component}'
        else:
            title = f'Channel_{component}'
        axes[i].set_title(title, fontsize=10)
        axes[i].grid()
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=100)
    plt.close(fig)


def plot_spectrums(data: np.ndarray, output_folder: str, output_name: str,
                   components_order=('X', 'Y', 'Z'),
                   freq_lims=(0, 10)) -> None:
    data = data[(data[:, 0] >= freq_lims[0]) * (data[:, 0] <= freq_lims[1])]
    fig, axes = plt.subplots(3, 1)
    fig.set_size_inches(15, 15)
    fig.dpi = 96
    for i, component in enumerate(components_order):
        axes[i].plot(data[:, 0], data[:, 2 * i + 1], lw=1, color='#000000',
                     label='Original')
        axes[i].plot(data[:, 0], data[:, 2 * (i + 1)], lw=2, color='#FF0000',
                     label='Smoothed')
        axes[i].set_xlim(freq_lims[0], freq_lims[-1])
        axes[i].set_xlabel('Frequency, Hz')
        axes[i].set_ylabel('Amplitude, c.u')
        axes[i].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        if i == 0:
            title = f'{output_name}\nChannel_{component}'
        else:
            title = f'Channel_{component}'
        axes[i].set_title(title, fontsize=10)
        axes[i].grid()
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=100)
    plt.close(fig)


def plot_correlation(device_list: list, colors,
                     correlation_matrix: np.ndarray,
                     output_folder: str, output_name: str) -> None:
    """
    Plotting general graph with all correlationf for devices
    :param device_list: list of file names
    :param colors: graph colors
    :param correlation_matrix: correlation matrix
    :param output_folder: export folder
    :param output_name: export name
    :return: None
    """
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.8
    mpl.rcParams['figure.subplot.bottom'] = 0.3
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()

    fig.set_size_inches(13, 10)
    fig.dpi = 96
    axes = fig.add_subplot(111)

    axes.set_ylim(0, 1)

    graph_count = len(device_list)

    x_values = np.arange(1, graph_count + 1, 1)
    x_labels = [x[:17] +'...' for x in device_list]

    axes.set_xticks(x_values)
    axes.set_xticklabels(x_labels, minor=False, rotation=90)

    for i in range(graph_count):
        coeffs = correlation_matrix[i, :]
        color = '#%02X%02X%02X' % colors[i]
        axes.plot(x_values, coeffs, label=x_labels[i], color=color, lw=1)

    x_label = 'Devices'
    y_label = 'Correlation coefficient value'
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    axes.grid()

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=150)
    plt.close(fig)
