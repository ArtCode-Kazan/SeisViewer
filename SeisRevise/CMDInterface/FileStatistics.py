import warnings
import sys

from SeisCore.GeneralFunction.cmdLogging import print_message

from SeisRevise.Functions.Processing import files_info
from SeisRevise.DBase.SqliteDBase import SqliteDB


def file_stats():
    """
    Функция для получения информации о bin-файлах в папке
    :return: None
    """
    # -----------------------------------------------------------------------
    # блок отладки
    # dbase_folder_path = r'D:\AppsBuilding\Packages\GUISeisRevise'
    # dbase_name = 'session.db'
    # конец блока отладки
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # блок релиза
    warnings.filterwarnings("ignore")
    parameters = sys.argv
    # проверка числа параметров
    if len(parameters) != 3:
        print('Неверное число параметров')
        return None
    # dbase directory path
    dbase_folder_path = parameters[1]
    # dbase_name
    dbase_name = parameters[2]
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

    # получение информации по файлам в рабочей папке
    general_data = tables.gen_data
    statistic_data = tables.file_stats
    db_gen_data = general_data.get()

    # путь к рабочей папке
    directory_path = db_gen_data.work_dir
    print_message(text='Получение информации о файлах...', level=0)
    files_data = files_info(directory_path=directory_path)
    # запись данных в таблицу БД сессии
    statistic_data.delete().execute()
    for data_dict in files_data:
        statistic_data.create(**data_dict)
    print_message(text='Информация о файлах получена. Всего найдено {} '
                       'файлов'.format(len(files_data)), level=0)
