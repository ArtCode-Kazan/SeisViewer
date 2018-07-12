import numpy as np
import os


def part_of_signal_to_file(signal, output_folder,
                           output_name):
    """
    Функция записи участка данных сигнала в текстовый dat файл
    :param signal: одномерный массив numpy
    :param output_folder: папка сохранения результата
    :param output_name: имя файла (без расширения)
    :return: None

    """
    export_path = os.path.join(output_folder, output_name+'.dat')
    np.savetxt(fname=export_path, X=signal,fmt='%i')


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
    export_path = os.path.join(output_folder, output_name+'.dat')
    f = open(export_path, 'w')
    for line in write_lines:
        f.write(line)
    f.close()


def spectrum_to_file(frequency, amplitude, type, output_folder, output_name):
    """
    Функция для экспорта данных сглаженного и НЕсглаженного спектров в виде
    файла
    :param frequency: массив с набором частот
    :param amplitude: массив с набором амплитуд
    :param type: тип спектра (сглаженный или несглаженный)
    :param output_folder: папка экспорта
    :param output_name: имя файла (БЕЗ РАСШИЕРЕНИЯ!)
    :return: None
    """
    if type=='.smooth':
        extension = 'ssc'
    elif type=='no_smooth':
        extension = '.sc'
    else:
        extension = '.dat'
    export_path = os.path.join(output_folder, output_name + extension)
    np.savez(export_path, frequency, amplitude)


