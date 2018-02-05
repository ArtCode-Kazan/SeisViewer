import os


def correlation_to_file(devices, correlation_matrix,output_folder,
                        output_name):
    """
    Функция для записи корреляционной матрицы в файл
    :param devices: список приборов
    :param correlation_matrix: корреляционная матрица
    :param output_folder: папка, куда будет сохранен файл
    :param output_name: имя файла
    :return: None

    """
    write_lines = list()
    header = 'NULL\t' + '\t'.join(devices) + '\n'
    write_lines.append(header)

    for i in range(correlation_matrix.shape[0]):
        t = list()
        t.append(devices[i])
        for j in range(correlation_matrix.shape[1]):
            t.append(str(correlation_matrix[i, j]))
        s = '\t'.join(t) + '\n'
        write_lines.append(s)

    filepath = os.path.join(output_folder,output_name+'.dat')
    f = open(filepath, 'w')
    for line in write_lines:
        f.write(line)
    f.close()
