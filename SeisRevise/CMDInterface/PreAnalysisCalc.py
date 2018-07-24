import sys
import os
import warnings

from SeisCore.GeneralFunction.cmdLogging import print_message

from SeisPars.Refactoring.BinaryFile import BinaryFile

from SeisRevise.DBase.SqliteDBase import SqliteDB
from SeisRevise.Functions.Processing import files_info
from SeisRevise.Functions.Exporting import part_of_signal_to_file
from SeisRevise.Functions.Plotting import plot_spectrogram
from SeisRevise.Functions.Plotting import plot_simple_spectrum
from SeisRevise.Functions.Plotting import plot_signal


def pre_analysis_calc():
    """
    Функция для расчета предварительного анализа сигналов
    :return: void
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
    is_correct, error = dbase.check_gen_data_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Общие данные успешно проверены", level=0)

    is_correct, error = dbase.check_pre_analysis_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Данные для проведения преданализа успешно проверены",
                  level=0)

    # get data from dbase
    tables, error = dbase.get_orm_model
    if tables is None:
        print(error)
        return None
    print_message(text='ORM-модель успешно получена', level=0)
    print_message(text='Чтение исходных параметров сессии...', level=0)
    general_data = tables.gen_data
    pre_analysis_data = tables.pre_analysis
    db_gen_data = general_data.get()
    db_panalysis_data = pre_analysis_data.get()

    # путь к рабочей папке
    directory_path = db_gen_data.work_dir
    # частота ресемплирования
    resample_frequency = db_gen_data.resample_frequency
    # компоненты для анализа
    components = list()
    if db_gen_data.x_component_flag:
        components.append('X')
    if db_gen_data.y_component_flag:
        components.append('Y')
    if db_gen_data.z_component_flag:
        components.append('Z')

    # минимальная секунда чистого сигнала
    left_time_edge = db_panalysis_data.left_edge
    # максимальная секунда чистого сигнала
    right_time_edge = db_panalysis_data.right_edge
    # параметр медианного фильтра
    if not db_panalysis_data.median_filter_flag:
        median_filter_parameter = None
    else:
        median_filter_parameter = db_panalysis_data.median_filter_parameter
    # параметр marmett фильтра
    if not db_panalysis_data.marmett_filter_flag:
        marmett_filter_parameter = None
    else:
        marmett_filter_parameter = db_panalysis_data.marmett_filter_parameter

    # минимальная частота визуализации
    min_frequency_visuality = db_panalysis_data.f_min_visual
    # максимальная частота визуализации
    max_frequency_visuality = db_panalysis_data.f_max_visual

    # вывод выборки сигнала в файл
    is_selection_signal_to_file = db_panalysis_data.select_signal_to_file_flag
    # вывод выборки сигнала в виде графика
    is_selection_signal_to_graph = \
        db_panalysis_data.select_signal_to_graph_flag
    # вывод спектров
    is_spectors = db_panalysis_data.separated_spectrums_flag
    # вывод 2D спектрограммы
    is_spectrogram = db_panalysis_data.spectrogram_flag
    print_message(text='Чтение исходных параметров сессии завершено', level=0)

    # анализ папки с данными сверки - получение полных путей к bin-файлам
    print_message('Анализ выбранной папки...', 0)
    bin_files_data = files_info(directory_path=directory_path)

    # вывод ошибок построения списка путей к bin-файлам
    if len(bin_files_data) == 0:
        print_message('Анализ папки завершен. Bin-файлов не найдено. '
                      'Обработка прервана', 0)
        return None
    else:
        print_message('Анализ папки завершен. Всего найдено {} '
                      'файлов'.format(len(bin_files_data)), 0)

    # проверка, что у всех файлов одинаковая частота и файлы корректны
    signal_frequency = None
    for file_data in bin_files_data:
        if file_data['error_text'] != 'ok':
            print_message(text='Ошибка обработки файла {}'.format(
                file_data['name']), level=1)
            print_message(text=file_data['error_text'], level=1)
            return None

        if signal_frequency is None:
            signal_frequency = file_data['frequency']
        else:
            if signal_frequency != file_data['frequency']:
                print_message('Файлы имеют разную частоту записи. '
                              'Обработка невозможна. Проверьте статистику '
                              'по файлам', 0)
                return None

    # создание папки с результатами расчетов
    folder_with_result = None
    for i in range(99):
        folder_name = 'PreAnalysis_vers_{}'.format(i + 1)
        folder_with_result = os.path.join(directory_path, folder_name)
        if not os.path.exists(folder_with_result):
            os.mkdir(folder_with_result)
            break
    print_message('Начат процесс предварительного анализа...', 0)
    # расчет длины выборки сигнала в отсчетах
    # получение номеров отсчетов для извлечения куска сигнала из файла (
    # БЕЗ РЕСЕМПЛИРОВАНИЯ!!!)
    start_moment_position = left_time_edge * signal_frequency
    end_moment_position = right_time_edge * signal_frequency - 1

    # получение номеров отсчетов для извлечения куска сигнала из файла (
    # ПОСЛЕ РЕСЕМПЛИРОВАНИЯ!!!)
    resample_parameter = resample_frequency / signal_frequency

    start_moment_position_resample = \
        int(start_moment_position * resample_parameter)
    end_moment_position_resample = \
        int(end_moment_position * resample_parameter)

    selection_size \
        = end_moment_position_resample - start_moment_position_resample + 1

    # запуск процесса извлечения выборок сигналов
    for file_number, file_data in enumerate(bin_files_data):
        # получение имени файла
        bin_file_name = file_data['name']

        print_message('Чтение файла {}...'.format(bin_file_name), 1)

        # Создание объекта для считывания файла
        bin_data = BinaryFile()
        bin_data.path = file_data['path']
        bin_data.resample_frequency = resample_frequency
        bin_data.start_moment = start_moment_position
        bin_data.end_moment = end_moment_position

        x_channel_number, y_channel_number, z_channel_number = bin_data.components_index

        signal = bin_data.signals
        # проверка, что сигнал извлечен и его длина равна требуемой
        # длине куска
        # проверка, что сигнал извлечен и его длина равна требуемой
        # длине куска
        if signal is None:
            print_message('Выборка файла пуста или имеет неверную длину. '
                          'Обработка прервана', 1)
            return None

        # если сигнал не пуст, второй цикл продолжает работу

        # Построение 2D-спектрограмм и простых (НЕ КУМУЛЯТИВНЫХ!!!) спектров
        for component in components:
            # определение индекса канала компоненты исходя из текущей
            #  компоненты
            if component == 'X':
                channel_number = x_channel_number
            elif component == 'Y':
                channel_number = y_channel_number
            elif component == 'Z':
                channel_number = z_channel_number
            else:
                print_message('Ошибка чтения номера компоненты. '
                              'Обработка прервана', 3)
                return None
            # запись выборки сигнала в файл
            if is_selection_signal_to_file:
                dat_file_name = '{}_ClearSignal_{}_Component'.format(
                    bin_file_name, component)
                # создание папки для сохранения результатов
                output_folder = os.path.join(folder_with_result, bin_file_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)
                part_of_signal_to_file(signal=signal[:, channel_number],
                                       output_folder=output_folder,
                                       output_name=dat_file_name)
                print_message('Выборка сигнала (файл {}, компонента {}) '
                              'записана'.format(bin_file_name, component), 3)

            # визуализация выборки сигнала в виде графика
            if is_selection_signal_to_graph:
                png_file_name = '{}_Signal_{}_Component_Graph'.format(
                    bin_file_name, component)
                # создание папки для сохранения результатов
                output_folder = os.path.join(folder_with_result, bin_file_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)
                plot_signal(time_start_sec=left_time_edge,
                            frequency=resample_frequency,
                            signal=signal[:, channel_number],
                            label=png_file_name,
                            output_folder=output_folder,
                            output_name=png_file_name)
                print_message('График выборки сигнала (файл {}, '
                              'компонента {}) построен'.format(
                                bin_file_name, component), 3)

            # построение спектров
            if is_spectors:
                png_file_name = '{}_SimpleSpectrum_{}_Component_' \
                                'Graph'.format(bin_file_name, component)
                # создание папки для сохранения результатов
                output_folder = os.path.join(folder_with_result, bin_file_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)
                plot_simple_spectrum(
                    signal=signal[:, channel_number],
                    frequency=resample_frequency,
                    median_filter_parameter=median_filter_parameter,
                    marmett_filter_parameter=marmett_filter_parameter,
                    f_min=min_frequency_visuality,
                    f_max=max_frequency_visuality,
                    output_folder=output_folder,
                    output_name=png_file_name)
                print_message('Спектр (файл {}, компонента {}) '
                              'построен'.format(bin_file_name, component), 3)

            # построение спектрограммы
            if is_spectrogram:
                # имя для png-файла складывается как название компоненты
                #  имя bin-файла+начальная секудна интервала+конечная
                # секунда интервала
                output_file_name = '{}_Component_{}_{}-{}_sec'.format(
                    component, bin_file_name, left_time_edge, right_time_edge)
                # создание папки для сохранения результатов
                output_folder = os.path.join(folder_with_result, bin_file_name)
                if not os.path.isdir(output_folder):
                    os.mkdir(output_folder)

                plot_spectrogram(
                    signal=signal[:, channel_number],
                    frequency=resample_frequency,
                    time_start_sec=left_time_edge,
                    min_frequency_visulize=min_frequency_visuality,
                    max_frequency_visualize=max_frequency_visuality,
                    output_folder=output_folder,
                    output_name=output_file_name)
                print_message('Спектрограмма (файл {}, компонента {}) '
                              'построена'.format(bin_file_name, component), 3)
    print_message('Обработка завершена', 0)
