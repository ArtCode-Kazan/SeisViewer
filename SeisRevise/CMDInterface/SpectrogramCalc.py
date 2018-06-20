import sys
import os

from SeisCore.GeneralFunction.cmdLogging import print_message

from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal7 as rsf7
from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal8 as rsf8

from SeisRevise.DBase.SqliteDBase import SqliteDB
from SeisRevise.Functions.Processing import export_folder_generate
from SeisRevise.Functions.Processing import get_bin_files
from SeisRevise.Functions.Plotting import plot_spectrogram


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
    # тип файла
    file_type = db_gen_data.file_type
    # тип записи
    record_type = db_gen_data.record_type
    # частота записи сигнала
    signal_frequency = db_gen_data.signal_frequency
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
    # временной интервал построения спектрограмм
    time_interval = db_spec_data.time_interval
    # размер окна построения спектрограмм
    window_size = db_spec_data.window_size
    # размер сдвига окна для
    noverlap_size = db_spec_data.noverlap_size
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

    # парсинг типа записи
    x_channel_number = record_type.index('X')
    y_channel_number = record_type.index('Y')
    z_channel_number = record_type.index('Z')

    # запуск процесса построения спектрограмм

    # главный цикл - по интервалам времени
    # ВНИМАНИЕ! Цикл бесконечный, так как неивестна длина данных в файле
    #  заранее - файл может быть очень большим настолько, что нельзя его
    #  полностью считать в память

    # номер интервала для обработки. Один интервал может быть равен
    # нескольким часам
    interval_number = 0
    while True:
        print_message(text='Начата обработка временного '
                           'интервала #{}...'.format(interval_number + 1),
                      level=1)
        # размер извлекаемого куска сигнала БЕЗ РЕСЕМПЛИРОВАНИЯ!!!
        signal_part_size = int(time_interval * 3600 * signal_frequency)

        # получение номеров отсчетов для извлечения куска сигнала из
        # файла БЕЗ РЕСЕМПЛИРОВАНИЯ!!!
        start_moment_position = interval_number * signal_part_size
        end_moment_position = start_moment_position + signal_part_size - 1

        # интервал секунд (нужно для названия выходного png-файла
        # картинки спектрограммы)
        start_second = int(time_interval * 3600) * interval_number
        end_second = start_second + int(time_interval * 3600)

        # второй цикл - по bin-файлам

        # переменная для определения прерывания бесконечного цикла -
        # True - если цикл нужно продолжить, False - если прерывать цикл
        # не нужно. Все зависит от того, есть ли извлеченный кусок
        # сигнала хотя бы в одном файле
        is_check_marker = False
        for file_path in bin_files_list:
            # получение имени файла
            bin_file_name = os.path.split(file_path)[-1].split('.')[0]
            print_message(text='Обработка файла {}...'.format(bin_file_name),
                          level=2)

            # проба считать данные в указанном интервале
            if file_type == 'Baikal7':
                signal = rsf7(file_path=file_path,
                              only_signal=True,
                              resample_frequency=resample_frequency,
                              start_moment=start_moment_position,
                              end_moment=end_moment_position)
            elif file_type == 'Baikal8':
                signal = rsf8(file_path=file_path,
                              signal_frequency=signal_frequency,
                              only_signal=True,
                              resample_frequency=resample_frequency,
                              start_moment=start_moment_position,
                              end_moment=end_moment_position)
            else:
                signal = None

            # если сигнал не пустой, добавляем (логическое OR) True
            if signal is not None:
                is_check_marker += True
                print_message(text='Выборка успешно считана', level=2)
            else:
                print_message(text='Выборка файла пуста. Обработка пропущена',
                              level=2)
                continue

            # если сигнал не пуст, второй цикл продолжает работу

            # Построение спектрограмм по компонентам
            for component in components:
                # имя для png-файла складывается как название компоненты
                #  имя bin-файла+начальная секудна интервала+конечная
                # секунда интервала
                output_file_name = '{}_Component_{}_{}-{}_sec'.format(
                    component, bin_file_name, start_second, end_second)

                # генерация пути к папке, куда будет сохраняться результат
                # в зависимости от типа структуры папок экспорта
                export_folder = export_folder_generate(
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
                    channel_number = x_channel_number
                elif component == 'Y':
                    channel_number = y_channel_number
                elif component == 'Z':
                    channel_number = z_channel_number
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
                             'компонента {}, временной интервал {}-{}. '
                             'Возможно, неверные параметры построения. '
                             'Обработка прервана'.format(
                                bin_file_name, component, start_second,
                                end_second),
                        level=3)
                    return None
                else:
                    print_message(
                        text='Спектрограмма (файл {}, компонента {}) '
                             'построена'.format(bin_file_name, component),
                        level=3)
            print_message(text='Файл {} обработан'.format(bin_file_name),
                          level=2)

        # проверка, нужно ли прервать бесконечный цикл
        if not is_check_marker:
            print_message(text='Построение спектрограмм завершено', level=0)
            break
        interval_number += 1
