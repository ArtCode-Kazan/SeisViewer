import warnings
import sys
import os

from SeisCore.GeneralFunction.cmdLogging import print_message

from SeisRevise.DBase.SqliteDBase import SqliteDB
from SeisRevise.Functions.Processing import read_coords_file


def join_coords():
    """
    Функция для присоединения координат точек из внешнего файла
    :return:
    """
    # -----------------------------------------------------------------------
    # блок отладки
    # dbase_folder_path = r'D:\AppsBuilding\Packages\GUISeisRevise'
    # dbase_name = 'session.db'
    # coords_file_path = r'D:\AppsBuilding\TestingData\BinData\coords.dat'
    # конец блока отладки
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # блок релиза
    warnings.filterwarnings("ignore")
    parameters = sys.argv
    # проверка числа параметров
    if len(parameters) != 4:
        print('Неверное число параметров')
        return None
    # dbase directory path
    dbase_folder_path = parameters[1]
    # dbase_name
    dbase_name = parameters[2]
    # file with coordinates
    coords_file_path = parameters[3]
    # конец блока релиза
    # -----------------------------------------------------------------------
    print_message(text="Подключение к БД сессии...", level=0)
    dbase = SqliteDB()
    dbase.folder_path = dbase_folder_path
    dbase.dbase_name = dbase_name
    print_message(text="Строка подключения к БД сформирована", level=0)

    # check dbase
    print_message(text="Проверка данных сессии...", level=0)
    is_correct, error = dbase.check_gen_data_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Общие данные успешно проверены", level=0)

    # get data from dbase
    print_message(text="Получение ORM-модели...", level=0)
    tables, error = dbase.get_orm_model
    if tables is None:
        print(error)
        return None
    print_message(text='ORM-модель успешно получена', level=0)

    # получение информации по файлам
    statistic_data = tables.file_stats

    # проверка количества записей в БД
    record_amount = statistic_data.select().count()
    if record_amount == 0:
        print_message(text='Отсутсвуют данные ORM для присвоения координат',
                      level=0)
        return None

    # чтение внешнего файла с координатами
    print_message(text='Начат процесс присоединения файла координат...',
                  level=0)
    if not os.path.exists(coords_file_path):
        print_message(text='Внешний файл координат не найден', level=0)
        return None
    outfile_data = read_coords_file(file_path=coords_file_path)
    if outfile_data is None:
        print_message(text='Ошибка чтения внешнего файла', level=0)
        return None

    # Присвоение координат для точек из БД сессии
    for file_data in statistic_data.select():
        point_name = file_data.point
        for point, x, y in outfile_data:
            if point == point_name:
                file_data.x_coord = x
                file_data.y_coord = y
                file_data.save()
                break
    print_message(text='Присоединение координат успешно завершено', level=0)
