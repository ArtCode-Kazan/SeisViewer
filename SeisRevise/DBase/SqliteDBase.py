import os
from peewee import *
import sqlite3


class SqliteDB:
    def __init__(self):
        self.__folder_path = None
        self.__dbase_name = None

    @property
    def folder_path(self):
        return self.__folder_path

    @folder_path.setter
    def folder_path(self, value):
        if len(value) > 0:
            if os.path.isdir(value):
                self.__folder_path = value

    @property
    def dbase_name(self):
        return self.__dbase_name

    @dbase_name.setter
    def dbase_name(self, value):
        if len(value) > 0:
            name, extension = value.split('.')
            if extension == 'db':
                self.__dbase_name = value

    @property
    def _is_correct_fields(self):
        errors = list()
        if self.folder_path is None:
            errors.append('Неверный путь к БД сессии')
        if self.dbase_name is None:
            errors.append('Неверное имя БД')

        if len(errors) == 0:
            return True, None
        else:
            error = '\n'.join(errors)
            return False, error

    @property
    def _get_full_path(self):
        is_correct, error = self._is_correct_fields
        if not is_correct:
            return None, error
        else:
            full_path = os.path.join(self.folder_path, self.dbase_name)
            return full_path, None

    @property
    def _get_connection(self):
        full_path, error = self._get_full_path
        if full_path is None:
            return None, error
        else:
            sqlite_db = SqliteDatabase(full_path)
            return sqlite_db, None

    @property
    def get_orm_model(self):
        connection, error = self._get_connection
        if connection is None:
            return None, error

        class BaseModel(Model):
            class Meta:
                database = connection

        # модель - общие данные для обработки
        class GeneralData(BaseModel):
            work_dir = CharField(verbose_name="Рабочая директория")
            file_type = CharField(verbose_name="Тип файлов")
            record_type = CharField(verbose_name="Тип записи")
            signal_frequency = IntegerField(
                verbose_name="Частота записи сигнала")
            resample_frequency = IntegerField(
                verbose_name="Частота ресемплирования")
            no_resample_flag = BooleanField(verbose_name="Нет ресемплирования")
            x_component_flag = BooleanField(verbose_name="x-component")
            y_component_flag = BooleanField(verbose_name="y-component")
            z_component_flag = BooleanField(verbose_name="z-component")

            # мета-класс модели
            class Meta:
                db_table = "GeneralData"

        # модель - 2D-спектрограммы
        class SpectrogramData(BaseModel):
            time_interval = FloatField(verbose_name="Интервал построения "
                                                    "спектрограмм, часы")
            window_size = IntegerField(verbose_name="Размер окна расчета")
            noverlap_size = IntegerField(verbose_name="Размер сдвига окна")
            f_min_visual = FloatField(verbose_name="Мин. частота визуализации")
            f_max_visual = FloatField(
                verbose_name="Макс. частота визуализации")
            folder_structure = CharField(
                verbose_name="Структура папки экспорта")

            # мета-класс модели
            class Meta:
                db_table = "SpectrogramData"

        # модель - расчет корреляций
        class CorrelationData(BaseModel):
            left_edge = IntegerField(
                verbose_name="Левая граница выборки куска сигнала, с")
            right_edge = IntegerField(
                verbose_name="Правая граница выборки куска сигнала, с")
            window_size = IntegerField(
                verbose_name="Размер окна расчета корреляций")
            noverlap_size = IntegerField(
                verbose_name="Сдвиг окна расчтеа корреляций")
            median_filter_parameter = IntegerField(
                verbose_name="Параметр медианного фильтра")
            median_filter_flag = BooleanField(
                verbose_name="Флаг использования медианного фильтра")
            marmett_filter_parameter = IntegerField(
                verbose_name="Параметр фильтра marmett")
            marmett_filter_flag = BooleanField(
                verbose_name="Флаг использования фильтра marmett")
            f_min_calc = FloatField(
                verbose_name="Минимальная частота расчета корреляции")
            f_max_calc = FloatField(
                verbose_name="Максимальная частота расчета корреляции")
            f_min_visual = FloatField(
                verbose_name="Минимальная частота визуализации")
            f_max_visual = FloatField(
                verbose_name="Максимальная частота визуализации")
            select_signal_to_file_flag = BooleanField(
                verbose_name="Флаг экспорта выборки сигнала в виде файла")
            select_signal_to_graph_flag = BooleanField(
                verbose_name="Флаг экспорта выборки сигнала в виде графика")
            separated_spectrums_flag = BooleanField(
                verbose_name="Флаг экспорта спектров сигналов каждого файла в "
                             "отдельности")
            general_spectrums_flag = BooleanField(
                verbose_name="Флаг экспорта общего графика со сглаженными "
                             "спектрами")
            correlation_matrix_flag = BooleanField(
                verbose_name="Флаг экспорта матрицы коэф-тов корреляции")
            correlation_graph_flag = BooleanField(
                verbose_name="Флаг экспорта коэф-тов корреляции в виде "
                             "графиков")
            correlation_separate_graph_flag = BooleanField(
                verbose_name='Флаг экспорта отдельных графиков коэф-та '
                             'корреляции')
            smooth_spectrum_data_flag = BooleanField(
                verbose_name='Флаг экспорта сглаженного спектра в виде файла '
                             '(весь набор частот)')
            no_smooth_spectrum_data_flag = BooleanField(
                verbose_name='Флаг экспорта НЕсглаженного спектра в виде '
                             'файла (весь набор частот)')

            # мета-класс модели
            class Meta:
                db_table = "CorrelationData"

        # модель - предварительный анализ
        class PreAnalysisData(BaseModel):
            left_edge = IntegerField(
                verbose_name="Левая граница выборки куска сигнала, с")
            right_edge = IntegerField(
                verbose_name="Правая граница выборки куска сигнала, с")
            window_size = IntegerField(
                verbose_name="Размер окна расчета спектрограммы")
            noverlap_size = IntegerField(
                verbose_name="Сдвиг окна расчета спектрограммы")
            median_filter_parameter = IntegerField(
                verbose_name="Параметр медианного фильтра")
            median_filter_flag = BooleanField(
                verbose_name="Флаг использования медианного фильтра")
            marmett_filter_parameter = IntegerField(
                verbose_name="Параметр фильтра marmett")
            marmett_filter_flag = BooleanField(
                verbose_name="Флаг использования фильтра marmett")
            f_min_visual = FloatField(
                verbose_name="Минимальная частота визуализации")
            f_max_visual = FloatField(
                verbose_name="Максимальная частота визуализации")
            select_signal_to_file_flag = BooleanField(
                verbose_name="Флаг экспорта выборки сигнала в виде файла")
            select_signal_to_graph_flag = BooleanField(
                verbose_name="Флаг экспорта выборки сигнала в виде графика")
            separated_spectrums_flag = BooleanField(
                verbose_name="Флаг экспорта спектров сигналов каждого файла в "
                             "отдельности")
            spectrogram_flag = BooleanField(
                verbose_name="Флаг экспорта файла спектрограммы")

            # мета-класс модели
            class Meta:
                db_table = "PreAnalysisData"

        class Tables:
            gen_data = GeneralData
            spectrograms = SpectrogramData
            correlations = CorrelationData
            pre_analysis = PreAnalysisData

        return Tables(), None

    @property
    def create_dbase(self):
        full_path, error = self._get_full_path
        if full_path is None:
            return False, error

        if os.path.exists(full_path):
            return False, 'БД сессии уже существует'

        # create empty dbase
        try:
            conn = sqlite3.connect(full_path)
            conn.close()
        except ConnectionError:
            return False, 'Ошибка создания БД'

        # create tables
        try:
            sqlite_db, errors = self._get_connection
            if sqlite_db is None:
                return False, errors
            tables, errors = self.get_orm_model
            if tables is None:
                return False, errors
            tabs_list = (tables.gen_data, tables.spectrograms,
                         tables.correlations, tables.pre_analysis)
            sqlite_db.connect()
            sqlite_db.create_tables(tabs_list, safe=True)
            return True, None
        except DatabaseError:
            return False, 'Ошибка создания таблиц БД'

    @property
    def check_gen_data_table(self):
        tables, errors = self.get_orm_model
        if tables is None:
            return False, errors

        general_data = tables.gen_data
        if general_data.select().count() != 1:
            error = 'Таблица GeneralData пуста или имеет неверное ' \
                    'количество записей'
            return False, error

        try:
            db_gen_data = general_data.get()
        except ValueError:
            error = 'Ошибка чтения таблицы GeneralData'
            return False, error

        if len(db_gen_data.work_dir) == 0:
            error = 'Путь к рабочей папке не задан'
            return False, error

        if not os.path.isdir(db_gen_data.work_dir):
            error = 'Путь к рабочей папке не существует'
            return False, error

        # проверка типа файла
        if db_gen_data.file_type not in ['Baikal7', 'Baikal8']:
            error = 'Неверно указан тип файла'
            return None, error

        # тип записи
        if db_gen_data.record_type not in ['ZXY', 'XYZ']:
            error = 'Неверно указан тип записи'
            return False, error

        # частота записи сигнала
        signal_frequency = db_gen_data.signal_frequency
        if signal_frequency <= 0:
            error = 'Не задана частота записи сигнала'
            return False, error

        resample_frequency = db_gen_data.resample_frequency
        if resample_frequency <= 0:
            error = 'Не задана частота ресемплирования'
            return False, error

        # проверка кратности частот ресемплирования и исходной частоты
        if signal_frequency % resample_frequency != 0:
            error = 'Частота ресемплирования должна быть кратной частоте ' \
                    'сигнала'
            return False, error

        # список компонент для анализа
        if not (
                db_gen_data.x_component_flag or db_gen_data.y_component_flag or
                db_gen_data.z_component_flag):
            error = 'Не выбрано ни одной компоненты для анализа'
            return False, error
        return True, None

    @property
    def check_spectrogram_table(self):
        tables, errors = self.get_orm_model
        if tables is None:
            return False, errors
        spectrogram_data = tables.spectrograms

        # check record count
        if spectrogram_data.select().count() != 1:
            error = 'Таблица SpectrogramData пуста или имеет неверное ' \
                    'количество записей'
            return False, error

        try:
            db_spec_data = spectrogram_data.get()
        except ValueError:
            error = 'Ошибка чтения таблицы SpectrogramData'
            return False, error

        # размер временного интервала (часы)
        if db_spec_data.time_interval <= 0:
            error = 'Не задан интервал построения спектрограмм'
            return False, error

        # размер окна расчета (отсчeты)
        if db_spec_data.window_size <= 0:
            error = 'Не задан размер окна построения спектрограмм'
            return False, error

        # размер сдвига окна (отсчеты)
        if db_spec_data.noverlap_size <= 0:
            error = 'Не задан размер сдвига окна построения спектрограмм'
            return False, error

        # минимальная частота для визуализации (Гц)
        min_frequency = db_spec_data.f_min_visual
        if min_frequency < 0:
            error = 'Не задана минимальная частота визуализации'
            return False, error

        # максимальная частота для визуализации (Гц)
        max_frequency = db_spec_data.f_max_visual
        if max_frequency <= 0:
            error = 'Не задана максимальная частота визуализации'
            return False, error

        # проверка частот на правильность указания
        if min_frequency > max_frequency:
            error = 'Неверно указан диапазон частот визуализации спектрограмм'
            return False, error

        # тип структуры экспорта результатов
        if db_spec_data.folder_structure not in \
                ['HourStructure', 'DeviceStructure']:
            error = 'Неверно указана структура экспорта результатов'
            return False, error
        return True, None

    @property
    def check_correlation_table(self):
        tables, errors = self.get_orm_model
        if tables is None:
            return False, errors

        correlation_data = tables.correlations
        # check record count
        if correlation_data.select().count() != 1:
            error = 'Таблица CorrelationData пуста или имеет неверное ' \
                    'количество записей'
            return False, error

        try:
            db_corr_data = correlation_data.get()
        except ValueError:
            error = 'Ошибка чтения таблицы CorrelationData'
            return False, error

        # левая граница выборки сигнала (секунда)
        if db_corr_data.left_edge < 0:
            error = 'Не задана левая граница выборки сигнала'
            return False, error

        # правая граница выборки сигнала (секунда)
        if db_corr_data.right_edge <= 0:
            error = 'Не задана правая граница выборки сигнала'
            return False, error

        # проверка на правильность указания границ чистого участка
        if db_corr_data.right_edge <= db_corr_data.left_edge:
            error = 'Неверно указан диапазон выборки сигнала'
            return False, error

        # размер окна расчета корреляций (отсчеты)
        if db_corr_data.window_size <= 0:
            error = 'Неверно указан размер окна расчета корреляций'
            return False, error

        # размер сдвига окна (отсчеты)
        if db_corr_data.noverlap_size <= 0:
            error = 'Неверно указан размер сдвига окна расчета корреляций'
            return False, error

        # параметр медианного фильтра
        if db_corr_data.median_filter_parameter <= 0:
            error = 'Неверно указан параметр медианного фильтра'
            return False, error

        # проверка, что параметр медианного фильтра нечетный
        if db_corr_data.median_filter_parameter % 2 == 0:
            error = 'Параметр медианного фильтра должен быть нечетным'
            return False, error

        # параметр фильтра marmett
        if db_corr_data.marmett_filter_parameter <= 0:
            error = 'Неверно указан параметр фильтра marmett'
            return False, error

        # проверка, что указан хотя бы один параметр фильтрации
        if not (db_corr_data.median_filter_flag or
                db_corr_data.marmett_filter_flag):
            error = 'Не указан ни один из параметров фильтрации'
            return False, error

        # минимальная частота для расчетов (Гц)
        if db_corr_data.f_min_calc < 0:
            error = 'Не указана минимальная частота для расчета корреляций'
            return False, error

        # максимальная частота для расчетов (Гц)
        if db_corr_data.f_max_calc <= 0:
            error = 'Не указана максимальная частота для расчета корреляций'
            return False, error

        # проверка пределов частот для расчета
        if db_corr_data.f_max_calc <= db_corr_data.f_min_calc:
            error = 'Неверно указаны пределы частот для анализа'
            return False, error

        # минимальная частота для визуализации (Гц)
        if db_corr_data.f_min_visual < 0:
            error = 'Не указана минимальная частота для визуализации спектров'
            return False, error

        # максимальная частота для визуализации (Гц)
        if db_corr_data.f_max_visual <= 0:
            error = 'Не указана максимальная частота для визуализации спектров'
            return False, error

        # проверка пределов частот для визуализации
        if db_corr_data.f_max_visual <= db_corr_data.f_min_visual:
            error = 'Неверно указан пределы частот для визуализации спектров'
            return False, error

        # проверка, что хотя бы один из файлов экспорта выбран
        checking = db_corr_data.select_signal_to_file_flag or \
            db_corr_data.select_signal_to_graph_flag or \
            db_corr_data.separated_spectrums_flag or \
            db_corr_data.general_spectrums_flag or \
            db_corr_data.correlation_matrix_flag or \
            db_corr_data.correlation_graph_flag or \
            db_corr_data.correlation_separate_graph_flag or \
            db_corr_data.smooth_spectrum_data_flag or \
            db_corr_data.no_smooth_spectrum_data_flag
        if not checking:
            error = 'Не выбран ни один из способов экспорта результатов ' \
                    'данных по расчетам корреляций'
            return False, error
        return True, None

    @property
    def check_pre_analysis_table(self):
        tables, errors = self.get_orm_model
        if tables is None:
            return False, errors

        pre_analysis_data = tables.pre_analysis
        # check record count
        if pre_analysis_data.select().count() != 1:
            error = 'Таблица CorrelationData пуста или имеет неверное ' \
                    'количество записей'
            return False, error

        try:
            db_analysis_data = pre_analysis_data.get()
        except ValueError:
            error = 'Ошибка чтения таблицы PreAnalysisData'
            return False, error

        # левая граница выборки сигнала (секунда)
        if db_analysis_data.left_edge < 0:
            error = 'Не задана левая граница выборки сигнала'
            return False, error

        # правая граница выборки сигнала (секунда)
        if db_analysis_data.right_edge <= 0:
            error = 'Не задана правая граница выборки сигнала'
            return False, error

        # проверка на правильность указания границ чистого участка
        if db_analysis_data.left_edge >= db_analysis_data.right_edge:
            error = 'Неверно указан диапазон выборки сигнала'
            return False, error

        # размер окна расчета спектрограммы (отсчеты)
        if db_analysis_data.window_size <= 0:
            error = 'Неверно указан размер окна расчета спектрограмм'
            return False, error

        # размер сдвига окна расчета спектрограммы(отсчеты)
        if db_analysis_data.noverlap_size <= 0:
            error = 'Неверно указан размер сдвига окна расчета спектрограмм'
            return False, error

        # параметр медианного фильтра
        if db_analysis_data.median_filter_parameter <= 0:
            error = 'Неверно задан параметр медианного фильтра'
            return False, error

        # проверка, что параметр медианного фильтра нечетный
        if db_analysis_data.median_filter_parameter % 2 == 0:
            error = 'Параметр медианного фильтра должен быть нечетным'
            return False, error

        # параметр фильтра marmett
        if db_analysis_data.marmett_filter_parameter <= 0:
            error = 'Неверно указан параметр фильтра marmett'
            return False, error

        # проверка, что указан хотя бы один параметр фильтрации
        if not (db_analysis_data.median_filter_flag or
                db_analysis_data.marmett_filter_flag):
            error = 'Не указан ни один из параметров фильтрации'
            return False, error

        # минимальная частота для визуализации (Гц)
        if db_analysis_data.f_min_visual < 0:
            error = 'Не указана минимальная частота для визуализации спектров'
            return False, error

        # максимальная частота для визуализации (Гц)
        if db_analysis_data.f_max_visual <= 0:
            error = 'Не указана максимальная частота для визуализации спектров'
            return False, error

        # проверка пределов частот для визуализации
        if db_analysis_data.f_min_visual >= db_analysis_data.f_max_visual:
            error = 'Неверно указан пределы частот для визуализации'
            return False, error

        # файлы для экспорта
        # проверка, что хотя бы один из файлов экспорта выбран
        checking = db_analysis_data.select_signal_to_file_flag or \
            db_analysis_data.select_signal_to_graph_flag or \
            db_analysis_data.separated_spectrums_flag or \
            db_analysis_data.spectrogram_flag
        if not checking:
            error = 'Не выбран ни один из способов экспорта результатов ' \
                    'данных по расчетам предварительного анализа'
            return False, error
        return True, None
