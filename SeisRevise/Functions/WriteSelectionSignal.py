import numpy as np
import os


def write_part_of_signal(signal, left_edge, output_folder,
                         output_name):
    """
    Функция записи участка данных сигнала в текстовый dat файл
    :param signal: одномерный массив numpy
    :param left_edge: номер первого отсчета сигнала
    :param output_folder: папка сохранения результата
    :param output_name: имя файла
    :return: None

    """
    # создание массива для записи указанного интервала в файл
    write_array = np.empty((signal.shape[0], 2),
                           dtype=np.float32)

    # генерация номеров отсчетов
    write_array[:, 0] = np.arange(left_edge, left_edge+signal.shape[0], 1)
    write_array[:, 1] = signal
    output_file_path=os.path.join(output_folder, output_name+'.dat')
    np.savetxt(fname=output_file_path, X=write_array,fmt='%i',delimiter='\t')
