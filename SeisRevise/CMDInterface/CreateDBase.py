import sys
import os
import warnings


from SeisCore.GeneralFunction.cmdLogging import print_message
from SeisRevise.DBase.SqliteDBase import SqliteDB


def create_dbase():
    """
    Функция для создания БД
    :return: None
    """
    # -----------------------------------------------------------------------
    # блок отладки
    # dbase_folder_path = r'D:\AppsBuilding\Packages\GUISeisRevise'
    # dbase_name = 'session.db'
    # replace_param = 'true'
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
    # replace parameter
    replace_param = parameters[3]
    # # конец блока релиза
    # -----------------------------------------------------------------------

    if replace_param == 'true':
        try:
            os.remove(os.path.join(dbase_folder_path, dbase_name))
        except os.error:
            print_message(text="Ошибка удаления БД предыдущей сессии", level=0)
            return None

    dbase = SqliteDB()
    dbase.folder_path = dbase_folder_path
    dbase.dbase_name = dbase_name

    is_success, error = dbase.create_dbase
    if not is_success:
        print_message(text=error, level=0)
    else:
        print_message(text="БД сессии успешно создана", level=0)
