import sys

from SeisCore.GeneralFunction.cmdLogging import print_message
from SeisRevise.DBase.SqliteDBase import SqliteDB


def create_dbase():
    """
    Функция для создания БД
    :return: None
    """
    # -----------------------------------------------------------------------
    # блок отладки
    dbase_folder_path = r'D:\AppsBuilding\Packages\GUISeisRevise\tmp'
    dbase_name = 'session.db'
    # конец блока отладки
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # блок релиза
    # parameters = sys.argv
    # # проверка числа параметров
    # if len(parameters) != 3:
    #     print('Неверное число параметров')
    #     return None
    # # dbase directory path
    # dbase_folder_path = parameters[1]
    # # dbase_name
    # dbase_name = parameters[2]
    # конец блока релиза
    # -----------------------------------------------------------------------

    dbase = SqliteDB()
    dbase.folder_path = dbase_folder_path
    dbase.dbase_name = dbase_name
    is_success, error = dbase.create_dbase
    if not is_success:
        print_message(text=error, level=0)
    else:
        print_message(text="БД сессии успешно создана", level=0)
