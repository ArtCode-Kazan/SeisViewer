import numpy as np
import os


def signal_to_file(signal_data: np.ndarray,
                   output_folder: str, output_name: str) -> None:
    """
    :param signal_data: columns Time, X, Y, Z channels
    :param output_folder:
    :param output_name:
    :return:
    """
    export_path = os.path.join(output_folder, output_name + '.dat')
    header = ['Time', 'X_channel', 'Y_channel', 'Z_channel']
    header = '\t'.join(header)
    fmt = '%.3f\t' * 4
    np.savetxt(fname=export_path, X=signal_data, fmt=fmt, header=header,
               comments='')


def spectrum_to_file(data: np.ndarray, output_folder: str, output_name: str):
    export_path = os.path.join(output_folder, output_name + '.dat')
    header = ['Frequency']
    for component in 'XYZ':
        header += [f'{component}_original', f'{component}_smooth']
    header = '\t'.join(header)
    fmt = '%.5f\t' + '%.3f\t' * 6
    np.savetxt(fname=export_path, X=data, fmt=fmt, delimiter='\t',
               header=header, comments='')


def correlation_to_file(devices, correlation_matrix, output_folder,
                        output_name):
    """
    Функция для записи корреляционной матрицы в файл
    :param devices: список приборов
    :param correlation_matrix: корреляционная матрица
    :param output_folder: папка, куда будет сохранен файл
    :param output_name: имя файла (без расширения)
    :return: None
    """
    # формирование заголовка столбцов
    header = 'NULL\t' + '\t'.join(devices) + '\n'
    # сборка строк для записив файл
    write_lines = list()
    write_lines.append(header)
    for i in range(correlation_matrix.shape[0]):
        t = list()
        t.append(devices[i])
        for j in range(correlation_matrix.shape[1]):
            t.append(str(correlation_matrix[i, j]))
        s = '\t'.join(t) + '\n'
        write_lines.append(s)
    # запись данных в файл
    export_path = os.path.join(output_folder, output_name + '.dat')
    f = open(export_path, 'w')
    for line in write_lines:
        f.write(line)
    f.close()
