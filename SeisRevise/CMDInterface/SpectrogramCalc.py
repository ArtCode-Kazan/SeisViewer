import sys
import os

from SeisCore.GeneralFunction.cmdLogging import print_message

from SeisPars.Classes.BinaryFile import BinaryFile

from SeisRevise.DBase.SqliteDBase import SqliteDB
from SeisRevise.Functions.Processing import get_bin_files
from SeisRevise.Functions.Plotting import plot_spectrogram


def _export_folder_generate(root_folder, structure_type, component,
                           bin_file_name=None, start_time_sec=None,
                           end_time_sec=None):
    """
    Функция для генерации пути папки для экспорта результатов
    :param root_folder: корневая папка всех сверочных данных
    :param structure_type: тип структуры папок - HourStructure (почасовая),
    DeviceStructure(поприборная)
    :param component: название компоненты сигнала (X, Y, Z)
    :param bin_file_name: имя bin-файла (без расширения)
    :param start_time_sec: начальная секунда расчета спектрограмм
    :param end_time_sec: конечная секунда расчета спектрограмм
    :return: путь к папке
    """
    # Проверка введенных параметров
    if structure_type == 'HourStructure' and (start_time_sec is None or
                                              end_time_sec is None):
        # если структура папки почасовая, то наличие начальной и конечной
        # секунд обязательно
        return None

    if structure_type == 'DeviceStructure' and bin_file_name is None:
        # если структура папки поприборная, то наличие имени bin-файла
        # обязательно
        return None

    # В случае, если структура папки организована как по часам
    # путь к папке складывается из корневой папки/2DSpectrograms/{}_component
    if structure_type == 'HourStructure':
        export_folder_path = os.path.join(
            root_folder,
            '2DSpectrograms',
            '{}-{}_sec'.format(start_time_sec, end_time_sec),
            '{}_component'.format(component))
    # В случае, если структура папки организована как по датчикам
    # путь к папке будет как:
    # корневая папка/папка с файлом датчика/{}_component
    elif structure_type == 'DeviceStructure':
        export_folder_path = os.path.join(
            root_folder,
            bin_file_name,
            '{}_component'.format(component))
    else:
        return None
    # создание папки для сохранения результатов
    if not os.path.exists(export_folder_path):
        os.makedirs(export_folder_path)

    # возвращение результата
    if os.path.exists(export_folder_path):
        return export_folder_path
    else:
        return None


def spectrogram_calc():
    """
    Функция для потокового построения спектрограмм
    :return: void
    """
    # -----------------------------------------------------------------------
    # блок отладки
    # dbase_folder_path = r'D:\AppsBuilding\Packages\GUISeisRevise\tmp'
    # dbase_name = 'session.db'
    # конец блока отладки
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # блок релиза
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
        resample_frequency = db_gen_data.resample_frequency
    else:
        resample_frequency = None
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
    # размер окна построения спектрограмм
    window_size = 8192
    # размер сдвига окна для
    noverlap_size = 256
    # частоты визуализации
    min_frequency = db_spec_data.f_min_visual
    max_frequency = db_spec_data.f_max_visual
    # получение структуры папок экспорта
    export_structure = db_spec_data.folder_structure
    print_message(text='Чтение исходных параметров сессии завершено', level=0)

    print_message(text='Начат процесс построения спектрограмм...', level=0)
    # анализ папки с данными сверки - получение полных путей к bin-файлам
    print_message(text='Анализ выбранной папки...', level=0)
    bin_files_list, error = get_bin_files(directory_path=directory_path)

    # вывод ошибок построения списка путей к bin-файлам
    if bin_files_list is None:
        print_message(text=error, level=0)
        return None

    if len(bin_files_list) == 0:
        print_message(text='Анализ папки завершен. Bin-файлов не найдено. '
                      'Обработка прервана', level=0)
        return None
    print_message(text='Анализ папки завершен. '
                       'Всего найдено {} файлов'.format(len(bin_files_list)),
                  level=0)

    # запуск процесса построения спектрограмм

    # главный цикл по файлам
    for bin_file in bin_files_list:
        # получение имени файла
        bin_file_name = os.path.split(bin_file)[-1].split('.')[0]
        print_message(text='Начата обработка файла {}...'.format(bin_file_name),
                      level=1)
        # Чтение файла
        bin_data = BinaryFile()
        bin_data.path = bin_file
        signal_frequency = bin_data.signal_frequency
        if db_gen_data.no_resample_flag:
            resample_frequency = signal_frequency

        if signal_frequency % resample_frequency == 0:
            bin_data.resample_frequency = resample_frequency
        else:
            print_message(text='Частота дискретизации сигнала некратна '
                               'частоте ресемплирования. Обработка файла '
                               'пропущена',
                          level=1)
            continue

        components_indexes = bin_data.components_index
        seconds_delay = bin_data.seconds_delay
        if components_indexes is None or seconds_delay is None or \
                signal_frequency is None:
            print_message(text='Ошибка чтения файла {}'.format(bin_file_name),
                level=1)
            continue

        # вычисление количества интервалов разбиения
        intervals_amount = int(seconds_delay / (time_interval * 3600)) + 1
        # размер извлекаемого куска сигнала в секундах
        part_seconds_size = int(time_interval * 3600)
        # размер извлекаемого куска сигнала в отсчетах
        signal_part_size = int(part_seconds_size * signal_frequency)

        for interval_number in range(intervals_amount):
            # получение номеров отсчетов для извлечения куска сигнала из
            start_moment_position = interval_number * signal_part_size
            end_moment_position = start_moment_position + signal_part_size - 1

            # интервал секунд (нужно для названия выходного png-файла
            # картинки спектрограммы)
            start_second = int(time_interval * 3600) * interval_number
            end_second = start_second + int(time_interval * 3600)

            print_message(
                text='Интервал {}-{} сек...'.format(start_second,end_second),
                level=2)

            # извлечение сигнала
            bin_data.start_moment = start_moment_position
            bin_data.end_moment = end_moment_position
            signal = bin_data.signals

            if signal is None:
                print_message(
                    text='Ошибка извлечения сигнала интервала {}-{} '
                         'сек'.format(start_second,end_second),
                    level=2)
                continue

            # Построение спектрограмм по компонентам
            for component in components:
                print_message(
                    text='Компонента {}...'.format(component),
                    level=3)
                # имя для png-файла складывается как название компоненты
                #  имя bin-файла+начальная секудна интервала+конечная
                # секунда интервала
                output_file_name = '{}_Component_{}_{}-{}_sec'.format(
                    component, bin_file_name, start_second, end_second)

                # генерация пути к папке, куда будет сохраняться результат
                # в зависимости от типа структуры папок экспорта
                export_folder = _export_folder_generate(
                    root_folder=directory_path,
                    structure_type=export_structure,
                    component=component,
                    bin_file_name=bin_file_name,
                    start_time_sec=start_second,
                    end_time_sec=end_second)

                # проверка создания каталога экспорта
                if export_folder is None:
                    print_message(text='Ошибка создания каталога экспорта. '
                                       'Обработка прервана', level=3)
                    return None

                # определение индекса канала компоненты исходя из текущей
                #  компоненты
                if component == 'X':
                    channel_number = components_indexes[0]
                elif component == 'Y':
                    channel_number = components_indexes[1]
                elif component == 'Z':
                    channel_number = components_indexes[2]
                else:
                    print_message(text='Ошибка чтения номера компоненты. '
                                       'Обработка прервана', level=3)
                    return None

                # построение спектрограммы
                is_create_spectrogram = plot_spectrogram(
                    signal=signal[:, channel_number],
                    frequency=resample_frequency,
                    window_size=window_size,
                    noverlap_size=noverlap_size,
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
                             'компонента {}, временной интервал {}-{} сек. '
                             'Возможно, неверные параметры построения. '
                             'Обработка прервана'.format(
                            bin_file_name, component, start_second,
                            end_second),
                        level=3)
                    return None
                else:
                    print_message(
                        text='Спектрограмма построена', level=3)
        print_message(text='Файл {} обработан'.format(bin_file_name),
                          level=2)
    print_message('Обработка завершена', 0)
