import sys
import os
import warnings

from SeisCore.GeneralFunction.cmdLogging import print_message

from SeisPars.Refactoring.BinaryFile import BinaryFile

from SeisRevise.DBase.SqliteDBase import SqliteDB
from SeisRevise.Functions.Processing import export_folder_generate
from SeisRevise.Functions.Processing import get_dates
from SeisRevise.Functions.Processing import files_info
from SeisRevise.Functions.Plotting import plot_spectrogram
from SeisRevise.Functions.Plotting import plot_signal


def spectrogram_calc():
    """
    Функция для потокового построения спектрограмм
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
    print_message(text="Проверка данных сессии...", level=0)
    is_correct, error = dbase.check_gen_data_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Общие данные успешно проверены", level=0)

    is_correct, error = dbase.check_spectrogram_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Данные для построения спектрограмм успешно проверены",
                  level=0)

    # get data from dbase
    print_message(text="Получение ORM-модели...", level=0)
    tables, error = dbase.get_orm_model
    if tables is None:
        print(error)
        return None
    print_message(text='ORM-модель успешно получена', level=0)
    print_message(text='Чтение исходных параметров сессии...', level=0)
    general_data = tables.gen_data
    spectrogram_data = tables.spectrograms
    db_gen_data = general_data.get()
    db_spec_data = spectrogram_data.get()

    # путь к рабочей папке
    directory_path = db_gen_data.work_dir
    # частота ресемплирования
    if not db_gen_data.no_resample_flag:
        resample_frequency = None
    else:
        resample_frequency = db_gen_data.resample_frequency
    # получение типа данных
    data_type = db_gen_data.data_type
    # компоненты для анализа
    components = list()
    if db_gen_data.x_component_flag:
        components.append('X')
    if db_gen_data.y_component_flag:
        components.append('Y')
    if db_gen_data.z_component_flag:
        components.append('Z')
    # временной интервал построения спектрограмм
    time_interval = db_spec_data.time_interval
    # частоты визуализации
    min_frequency = db_spec_data.f_min_visual
    max_frequency = db_spec_data.f_max_visual

    print_message(text='Чтение исходных параметров сессии завершено', level=0)

    # анализ папки с данными сверки - получение списка дат расчетов
    print_message(text='Анализ выбранной папки...', level=0)
    dates_list, error = get_dates(directory_path=directory_path)
    if dates_list is None:
        print_message(text=error, level=0)
        return None
    print_message(
        text='Количество дней для обработки: {}'.format(len(dates_list)),
        level=0)

    print_message(text='Начат процесс построения спектрограмм...', level=0)
    # первый цикл - обработка идет по дням
    for date_value in dates_list:
        print_message(text='Начата обработка дня: {}'.format(date_value),
                      level=0)

        current_directory = os.path.join(directory_path,
                                         date_value.strftime('%Y-%m-%d'))
        # анализ папки с данными текущего дня - получение полных путей к
        # bin-файлам
        bin_files_info = files_info(directory_path=current_directory)
        if len(bin_files_info) == 0:
            print_message(
                text='Анализ папки даты {} завершен. Bin-файлов не найдено. '
                     'Обработка пропущена'.format(date_value), level=0)
            continue
        print_message(
            text='Анализ папки даты {} завершен. '
                 'Всего найдено {} файлов'.format(date_value,
                                                  len(bin_files_info)),
            level=0)

        # запуск процесса построения спектрограмм
        # второй цикл - по файлам
        for file_info in bin_files_info:
            # проверка корректности файла
            if file_info['error_text'] != 'ok':
                print_message(text=file_info['error_text'], level=1)
                print_message(text='Обработка файла пропущена', level=1)
                continue
            # получение имени файла и пути
            bin_file_name = file_info['name']
            file_path = file_info['path']

            print_message(text='Обработка файла {}...'.format(bin_file_name),
                          level=1)
            # создание объекта Bin-файла для чтения
            bin_data = BinaryFile()
            bin_data.path = file_path
            # получение частоты записи сигнала
            signal_frequency = bin_data.signal_frequency
            # присваивание частоты ресемплирования
            if resample_frequency is None:
                resample_frequency = signal_frequency
            bin_data.resample_frequency = resample_frequency

            # получение индексов каналов записи
            x_channel_number, y_channel_number, z_channel_number = \
                bin_data.components_index
            # получение количества целых интервалов для построения спектрограмм
            time_duration_sec = bin_data.seconds_duration
            interval_amount = int(time_duration_sec/(3600*time_interval))+1
            print_message(text='Количество интервалов '
                               'для обработки: {}'.format(interval_amount),
                          level=1)
            # размер извлекаемого куска сигнала БЕЗ РЕСЕМПЛИРОВАНИЯ!!!
            signal_part_size = int(time_interval * 3600 * signal_frequency)
            # третий цикл - по интервалам времени
            for interval_number in range(interval_amount):
                print_message(
                   text='Обработка интервала #{}...'.format(interval_number+1),
                   level=2)
                # получение номеров отсчетов для извлечения куска сигнала из
                # файла БЕЗ РЕСЕМПЛИРОВАНИЯ!!!
                start_moment_position = interval_number * signal_part_size
                end_moment_position = \
                    start_moment_position + signal_part_size - 1
                # получение номера начальной и конечной секунды извлеченного
                #  куска
                start_second = int(interval_number * time_interval * 3600)
                end_second = start_second + int(time_interval * 3600)

                # установка границ для считывания сигнала
                bin_data.start_moment = start_moment_position
                bin_data.end_moment = end_moment_position

                # извлечение сигнала
                signal_data = bin_data.signals
                # проверка размера извлеченного куска сигнала
                if signal_data is None:
                    print_message(text='Выборка файла пуста или не '
                                       'соотвествует требуемому размеру. '
                                       'Обработка файла пропущена', level=3)
                    continue
                else:
                    print_message(text='Выборка успешно считана', level=3)

                # четвертый цикл - по компонентам
                for component in components:
                    print_message(
                        text='Обработка компоненты {}...'.format(component),
                        level=3)
                    # имя для png-файла складывается как название компоненты
                    #  имя bin-файла+начальная секудна интервала+конечная
                    # секунда интервала
                    output_file_name = '{}_Component_{}_{}-{}_sec'.format(
                        component, bin_file_name, start_second, end_second)

                    # генерация пути к папке, куда будет сохраняться результат
                    # в зависимости от типа структуры папок экспорта
                    export_folder = export_folder_generate(
                        root_folder=directory_path,
                        date_value=date_value,
                        data_type=data_type,
                        component=component,
                        bin_file_name=bin_file_name,
                        start_time_sec=start_second,
                        end_time_sec=end_second)

                    # проверка создания каталога экспорта
                    if export_folder is None:
                        print_message(
                            text='Ошибка создания каталога экспорта. '
                                 'Обработка прервана', level=4)
                        return None

                    # определение индекса канала компоненты исходя из текущей
                    #  компоненты
                    if component == 'X':
                        channel_number = x_channel_number
                    elif component == 'Y':
                        channel_number = y_channel_number
                    elif component == 'Z':
                        channel_number = z_channel_number
                    else:
                        print_message(text='Ошибка чтения номера компоненты. '
                                           'Обработка прервана', level=4)
                        return None

                    # построение спектрограммы
                    is_create_spectrogram = plot_spectrogram(
                        signal=signal_data[:, channel_number],
                        frequency=resample_frequency,
                        min_frequency_visulize=min_frequency,
                        max_frequency_visualize=max_frequency,
                        output_folder=export_folder,
                        output_name=output_file_name,
                        time_start_sec=start_second
                    )

                    # проверка создания спектрограммы
                    if not is_create_spectrogram:
                        print_message(
                            text='Ошибка построения спектрограммы: файл {}, '
                                 'компонента {}, временной интервал {}-{}. '
                                 'Возможно, неверные параметры построения. '
                                 'Обработка прервана'.format(
                                    bin_file_name, component, start_second,
                                    end_second),
                            level=4)
                        return None
                    else:
                        print_message(text='Спектрограмма построена', level=4)
                    # сохранение графика участка анализируемого сигнала в
                    # случае, если это данные МСИ
                    if data_type == 'MSI':
                        output_file_name = \
                            '{}_Signal_{}_{}-{}_sec'.format(
                                component, bin_file_name,
                                start_second, end_second)
                        plot_signal(time_start_sec=start_second,
                                    frequency=resample_frequency,
                                    signal=signal_data[:, channel_number],
                                    label=output_file_name,
                                    output_folder=export_folder,
                                    output_name=output_file_name)
                        print_message(
                            text='График участка сигнала построен', level=4)

            print_message(text='Файл {} обработан'.format(bin_file_name),
                          level=1)
        print_message(text='День {} обработан'.format(date_value), level=0)
    print_message(text='Построение спектрограмм завершено', level=0)
