from peewee import *


def get_orm_model(dbase_connection):
    class BaseModel(Model):
        class Meta:
            database = dbase_connection

    # модель - общие данные для обработки
    class GeneralData(BaseModel):
        work_dir = CharField(verbose_name="Рабочая директория")
        file_type = CharField(verbose_name="Тип файлов")
        record_type = CharField(verbose_name="Тип записи")
        signal_frequency = IntegerField(verbose_name="Частота записи сигнала")
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
        f_max_visual = FloatField(verbose_name="Макс. частота визуализации")
        folder_structure = CharField(verbose_name="Структура папки экспорта")

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
            verbose_name="Флаг экспорта коэф-тов корреляции в виде графиков")

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

    return GeneralData, SpectrogramData, CorrelationData, PreAnalysisData
