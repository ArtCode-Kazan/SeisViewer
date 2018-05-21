import sqlite3
import os
import sys
from peewee import *


from SeisCore.GeneralFunction.cmdLogging import error_format

from SeisRevise.DBase.ORM import get_orm_model


def create_dbase():
    parameters = sys.argv
    # проверка числа параметров
    if len(parameters) != 3:
        error_text = error_format(number=1,
                                  text='Неверное число параметров')
        print(error_text)
        return None

    # dbase directory path
    folder_path = parameters[1]
    # dbase_folder_path=r'D:\temp'
    # dbase_name
    dbase_name = parameters[2]
    # dbase_name =  'qweerrty'

    if not os.path.isdir(folder_path):
        return False
    # generate full path
    full_path = os.path.join(folder_path, dbase_name + '.db')

    # create empty dbase
    try:
        conn = sqlite3.connect(full_path)
        conn.close()
    except ConnectionError:
        return False

    # create tables
    try:
        sqlite_db = SqliteDatabase(full_path)
        tables = get_orm_model(dbase_connection=sqlite_db)
        sqlite_db.connect()
        sqlite_db.create_tables(tables, safe=True)
    except DatabaseError:
        return False
    return True


def check_dbase(folder_path, dbase_name, table_name):
    # generate full path
    full_path = os.path.join(folder_path, dbase_name + '.db')
    if not os.path.isdir(folder_path):
        print('SeisRevise Error 0x001: Не найдена БД')
        return False

    # get ORM
    sqlite_db = SqliteDatabase(full_path)
    general_data, spectrogram_data, correlation_data, pre_analysis_data = \
        get_orm_model(dbase_connection=sqlite_db)

    # check GeneralData
    if table_name == 'GeneralData':
        # check record count
        if general_data.select().count() != 1:
            print('SeisRevise Error 0x002: Таблица GeneralData пуста или '
                  'имеет неверное количество записей')
            return False

        try:
            db_gen_data = general_data.get()
        except ValueError:
            print('SeisRevise Error 0x034: Ошибка чтения таблицы '
                  'GeneralData')
            return False

        if len(db_gen_data.work_dir) == 0:
            print('SeisRevise Error 0x003: Путь к рабочей папке не задан')
            return False

        if not os.path.isdir(db_gen_data.work_dir):
            print('SeisRevise Error 0x003: Путь к рабочей папке не существует')
            return False

        # проверка типа файла
        if db_gen_data.file_type not in ['Baikal7', 'Baikal8']:
            print('SeisRevise Error 0x004: Неверно указан тип файла')
            return None

        # тип записи
        if db_gen_data.record_type not in ['ZXY', 'XYZ']:
            print('SeisRevise Error 0x005: Неверно указан тип записи')
            return False

        # частота записи сигнала
        signal_frequency = db_gen_data.signal_frequency
        if signal_frequency <= 0:
            print('SeisRevise Error 0x006: Не задана частота записи сигнала')
            return False

        resample_frequency = db_gen_data.resample_frequency
        if resample_frequency <= 0:
            print('SeisRevise Error 0x007: Не задана частота ресемплирования')
            return False

        # проверка кратности частот ресемплирования и исходной частоты
        if signal_frequency % resample_frequency != 0:
            print('SeisRevise Error 0x008: Частота ресемплирования должна '
                  'быть кратной частоте сигнала')
            return False

        # список компонент для анализа
        if not (
                db_gen_data.x_component_flag or db_gen_data.y_component_flag or
                db_gen_data.z_component_flag):
            print('SeisRevise Error 0x009: Не выбрано ни одной компоненты '
                  'для анализа')
            return False
        return True

    # check SpectrogramData
    if table_name == 'SpectrogramData':
        # check record count
        if spectrogram_data.select().count() != 1:
            print('SeisRevise Error 0x010: Таблица SpectrogramData пуста или '
                  'имеет неверное количество записей')
            return False

        try:
            db_spec_data = spectrogram_data.get()
        except ValueError:
            print('SeisRevise Error 0x034: Ошибка чтения таблицы '
                  'SpectrogramData')
            return False

        # размер временного интервала (часы)
        if db_spec_data.time_interval <= 0:
            print('SeisRevise Error 0x011: Не задан интервал построения '
                  'спектрограмм')
            return False

        # размер окна расчета (отсчeты)
        if db_spec_data.window_size <= 0:
            print('SeisRevise Error 0x012: Не задан размер окна построения '
                  'спектрограмм')
            return False

        # размер сдвига окна (отсчеты)
        if db_spec_data.noverlap_size <= 0:
            print('SeisRevise Error 0x013: Не задан размер сдвига окна '
                  'построения спектрограмм')
            return False

        # минимальная частота для визуализации (Гц)
        min_frequency = db_spec_data.f_min_visual
        if min_frequency < 0:
            print('SeisRevise Error 0x014: Не задана минимальная частота '
                  'визуализации')
            return False

        # максимальная частота для визуализации (Гц)
        max_frequency = db_spec_data.f_max_visual
        if max_frequency <= 0:
            print('SeisRevise Error 0x015: Не задана максимальная частота '
                  'визуализации')
            return False

        # проверка частот на правильность указания
        if min_frequency > max_frequency:
            print('SeisRevise Error 0x016: Неверно указан диапазон частот '
                  'визуализации спектрограмм')
            return False

        # тип структуры экспорта результатов
        if db_spec_data.folder_structure not in \
                ['HourStructure', 'DeviceStructure']:
            print('SeisRevise Error 0x017: Неверно указана структура '
                  'экспорта результатов')
            return False
        return True

    # check CorrelationData
    if table_name == 'CorrelationData':
        # check record count
        if correlation_data.select().count() != 1:
            print('SeisRevise Error 0x018: Таблица CorrelationData пуста или '
                  'имеет неверное количество записей')
            return False

        try:
            db_corr_data = correlation_data.get()
        except ValueError:
            print('SeisRevise Error 0x036: Ошибка чтения таблицы '
                  'CorrelationData')
            return False

        # левая граница выборки сигнала (секунда)
        if db_corr_data.left_edge < 0:
            print('SeisRevise Error 0x018: Не задана левая граница выборки '
                  'сигнала')
            return False

        # правая граница выборки сигнала (секунда)
        if db_corr_data.right_edge <= 0:
            print('SeisRevise Error 0x019: Не задана правая граница выборки '
                  'сигнала')
            return False

        # проверка на правильность указания границ чистого участка
        if db_corr_data.right_edge <= db_corr_data.left_edge:
            print('SeisRevise Error 0x020: Неверно указан диапазон выборки '
                  'сигнала')
            return False

        # размер окна расчета корреляций (отсчеты)
        if db_corr_data.window_size <= 0:
            print('SeisRevise Error 0x021: Неверно указан размер окна '
                  'расчета корреляций')
            return False

        # размер сдвига окна (отсчеты)
        if db_corr_data.noverlap_size <= 0:
            print('SeisRevise Error 0x022: Неверно указан размер сдвига окна '
                  'расчета корреляций')
            return False

        # параметр медианного фильтра
        if db_corr_data.median_filter_parameter <= 0:
            print('SeisRevise Error 0x023: Неверно указан параметр '
                  'медианного фильтра')
            return False

        # проверка, что параметр медианного фильтра нечетный
        if db_corr_data.median_filter_parameter % 2 == 0:
            print('SeisRevise Error 0x024: Параметр медианного фильтра '
                  'должен быть нечетным')
            return False

        # параметр фильтра marmett
        if db_corr_data.marmett_filter_parameter <= 0:
            print('SeisRevise Error 0x025: Неверно указан параметр '
                  'фильтра marmett')
            return False

        # проверка, что указан хотя бы один параметр фильтрации
        if not (db_corr_data.median_filter_flag or
                db_corr_data.marmett_filter_flag):
            print('SeisRevise Error 0x026: Не указан ни один из параметров '
                  'фильтрации')
            return False

        # минимальная частота для расчетов (Гц)
        if db_corr_data.f_min_calc < 0:
            print('SeisRevise Error 0x027: Не указана минимальная частота '
                  'для расчета корреляций')
            return False

        # максимальная частота для расчетов (Гц)
        if db_corr_data.f_max_calc <= 0:
            print('SeisRevise Error 0x028: Не указана максимальная частота '
                  'для расчета корреляций')
            return False

        # проверка пределов частот для расчета
        if db_corr_data.f_max_calc <= db_corr_data.f_min_calc:
            print('SeisRevise Error 0x029: Неверно указаны пределы частот для '
                  'анализа')
            return False

        # минимальная частота для визуализации (Гц)
        if db_corr_data.f_min_visual < 0:
            print('SeisRevise Error 0x030: Не указана минимальная частота '
                  'для визуализации спектров')
            return False

        # максимальная частота для визуализации (Гц)
        if db_corr_data.f_max_visual <= 0:
            print('SeisRevise Error 0x031: Не указана максимальная частота '
                  'для визуализации спектров')
            return False

        # проверка пределов частот для визуализации
        if db_corr_data.f_max_visual <= db_corr_data.f_min_visual:
            print('SeisRevise Error 0x032: Неверно указан пределы частот для '
                  'визуализации спектров')
            return False

        # проверка, что хотя бы один из файлов экспорта выбран
        checking = db_corr_data.select_signal_to_file_flag or \
            db_corr_data.select_signal_to_graph_flag or \
            db_corr_data.separated_spectrums_flag or \
            db_corr_data.general_spectrums_flag or \
            db_corr_data.correlation_matrix_flag or \
            db_corr_data.correlation_graph_flag
        if not checking:
            print("SeisRevise Error 0x033: Не выбран ни один из способов "
                  "экспорта результатов данных по расчетам корреляций")
            return False
        return True

    # check PreAnalysisData
    if table_name == 'PreAnalysisData':
        # check record count
        if pre_analysis_data.select().count() != 1:
            print('SeisRevise Error 0x018: Таблица CorrelationData пуста или '
                  'имеет неверное количество записей')
            return False

        try:
            db_analysis_data = pre_analysis_data.get()
        except ValueError:
            print('SeisRevise Error 0x036: Ошибка чтения таблицы '
                  'PreAnalysisData')
            return False

        # левая граница выборки сигнала (секунда)
        if db_analysis_data.left_edge < 0:
            print('SeisRevise Error 0x018: Не задана левая граница выборки '
                  'сигнала')
            return False

        # правая граница выборки сигнала (секунда)
        if db_analysis_data.right_edge <= 0:
            print('SeisRevise Error 0x018: Не задана правая граница выборки '
                  'сигнала')
            return False

        # проверка на правильность указания границ чистого участка
        if db_analysis_data.left_edge >= db_analysis_data.right_edge:
            print('SeisRevise Error 0x020: Неверно указан диапазон выборки '
                  'сигнала')
            return False

        # размер окна расчета спектрограммы (отсчеты)
        if db_analysis_data.window_size <= 0:
            print('SeisRevise Error 0x021: Неверно указан размер окна '
                  'расчета спектрограмм')
            return False

        # размер сдвига окна расчета спектрограммы(отсчеты)
        if db_analysis_data.noverlap_size <= 0:
            print('SeisRevise Error 0x022: Неверно указан размер сдвига окна '
                  'расчета спектрограмм')
            return False

        # параметр медианного фильтра
        if db_analysis_data.median_filter_parameter <= 0:
            print('SeisRevise Error 0x024: Неверно задан параметр медианного '
                  'фильтра')
            return False

        # проверка, что параметр медианного фильтра нечетный
        if db_analysis_data.median_filter_parameter % 2 == 0:
            print('SeisRevise Error 0x030: Параметр медианного фильтра должен'
                  ' быть нечетным')
            return False

        # параметр фильтра marmett
        if db_analysis_data.marmett_filter_parameter <= 0:
            print('SeisRevise Error 0x025: Неверно указан параметр '
                  'фильтра marmett')
            return False

        # проверка, что указан хотя бы один параметр фильтрации
        if not (db_analysis_data.median_filter_flag or
                db_analysis_data.marmett_filter_flag):
            print('SeisRevise Error 0x025: Не указан ни один из параметров '
                  'фильтрации')
            return False

        # минимальная частота для визуализации (Гц)
        if db_analysis_data.f_min_visual < 0:
            print('SeisRevise Error 0x030: Не указана минимальная частота '
                  'для визуализации спектров')
            return False

        # максимальная частота для визуализации (Гц)
        if db_analysis_data.f_max_visual <= 0:
            print('SeisRevise Error 0x031: Не указана максимальная частота '
                  'для визуализации спектров')
            return False

        # проверка пределов частот для визуализации
        if db_analysis_data.f_min_visual >= db_analysis_data.f_max_visual:
            print('SeisRevise Error 0x030: Неверно указан пределы частот для '
                  'визуализации')
            return False

        # файлы для экспорта
        # проверка, что хотя бы один из файлов экспорта выбран
        checking = db_analysis_data.select_signal_to_file_flag or \
            db_analysis_data.select_signal_to_graph_flag or \
            db_analysis_data.separated_spectrums_flag or \
            db_analysis_data.spectrogram_flag
        if not checking:
            print("SeisRevise Error 0x030: Не выбран ни один из способов "
                  "экспорта результатов данных по расчетам предварительного "
                  "анализа")
            return False
        return True
