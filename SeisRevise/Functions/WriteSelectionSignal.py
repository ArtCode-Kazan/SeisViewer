import numpy as np
import os


def write_part_of_signal(signal, output_folder,
                         output_name):
    """
    Функция записи участка данных сигнала в текстовый dat файл
    :param signal: одномерный массив numpy
    :param output_folder: папка сохранения результата
    :param output_name: имя файла
    :return: None

    """
    output_file_path=os.path.join(output_folder, output_name+'.dat')
    np.savetxt(fname=output_file_path, X=signal,fmt='%i')
