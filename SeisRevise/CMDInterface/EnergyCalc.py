import warnings
import sys
import numpy as np

from SeisCore.GeneralFunction.cmdLogging import print_message
from SeisCore.GeneralCalcFunctions.Spectrum import spectrum
from SeisCore.GeneralCalcFunctions.EnergyCalc import energy_calc as \
    calc_energy_by_spectrum

from SeisPars.Refactoring.BinaryFile import BinaryFile

from SeisRevise.DBase.SqliteDBase import SqliteDB
from SeisRevise.Functions.Exporting import energy_to_file


def energy_calc():
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

    is_correct, error = dbase.check_file_statistic_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Данные статистики файлов успешно проверены",
                  level=0)

    is_correct, error = dbase.check_energy_calc_table
    if not is_correct:
        print(error)
        return None
    print_message(text="Данные для расчета энергий успешно проверены",
                  level=0)

    # get data from dbase
    tables, error = dbase.get_orm_model
    if tables is None:
        print(error)
        return None
    print_message(text='ORM-модель успешно получена', level=0)
    print_message(text='Чтение исходных параметров сессии...', level=0)
    general_data = tables.gen_data
    energy_calc_data = tables.energy_calc
    file_statistics = tables.file_stats
    db_gen_data = general_data.get()
    db_energy_calc_data = energy_calc_data.get()

    # путь к рабочей папке
    directory_path = db_gen_data.work_dir
    # частота ресемплирования
    if not db_gen_data.no_resample_flag:
        resample_frequency = None
    else:
        resample_frequency = db_gen_data.resample_frequency
    # компоненты для анализа
    components = list()
    if db_gen_data.x_component_flag:
        components.append('X')
    if db_gen_data.y_component_flag:
        components.append('Y')
    if db_gen_data.z_component_flag:
        components.append('Z')

    # границы по времени для расчета (часы)
    left_edge = db_energy_calc_data.left_edge
    right_edge = db_energy_calc_data.right_edge
    # размер интервала по времени (часы)
    interval_size = db_energy_calc_data.interval
    # нулевое значение по умолчанию
    null_value = db_energy_calc_data.null_value
    # пределы частот для расчета
    f_min_calc = db_energy_calc_data.f_min_calc
    f_max_calc = db_energy_calc_data.f_max_calc
    print_message(text='Чтение исходных параметров сессии завершено', level=0)

    print_message(text='Начат процесс расчета энергий...', level=0)
    # количество компонент для анализа
    components_amount = len(components)
    # количество точек для расчета
    point_amount = file_statistics.select().count()
    # количество полных интервалов по времени
    interval_amount = int((right_edge - left_edge) // interval_size)

    # создание матрицы для сохранения результатов вычисления энергии
    energy_calc_result = np.empty(
        shape=(components_amount, point_amount, interval_amount),
        dtype=np.float)

    for file_index, file_data in enumerate(file_statistics.select()):
        print_message(
            text='Обработка точки {}...'.format(file_data.point),
            level=0)
        bin_data = BinaryFile()
        bin_data.path = file_data.path
        # получение частоты записи сигнала
        signal_frequency = bin_data.signal_frequency
        # переопределние частоты ресемплирования
        if resample_frequency is None:
            resample_frequency = signal_frequency
        bin_data.resample_frequency = resample_frequency
        # получение индексов каналов записи
        x_channel_number, y_channel_number, z_channel_number = \
            bin_data.components_index

        for interval_number in range(interval_amount):
            print_message(
                text='Обработка интервала #{}...'.format(interval_number + 1),
                level=1)
            left_interval_edge = left_edge + interval_number * interval_size
            right_interval_edge = left_interval_edge + interval_size
            # получение номеров отсчетов для извлечения куска сигнала из
            # файла БЕЗ РЕСЕМПЛИРОВАНИЯ!!!
            start_moment_position = \
                int(left_interval_edge * 3600 * signal_frequency)
            end_moment_position = \
                int(right_interval_edge * 3600 * signal_frequency) - 1
            bin_data.start_moment = start_moment_position
            bin_data.end_moment = end_moment_position

            # считывание сигнала
            signal_data = bin_data.signals
            if signal_data is None:
                print_message(text='Выборка файла пуста или не '
                                   'соотвествует требуемому размеру. '
                                   'Обработка файла пропущена', level=1)
                # Досрочное заполнение данных энергии значениями по умолчанию
                energy_calc_result[:, file_index, interval_number] = null_value
                continue
            else:
                print_message(text='Выборка успешно считана', level=1)

            # обработка по компонентам
            for component_index, component in enumerate(components):
                print_message(
                    text='Обработка компоненты {}...'.format(component),
                    level=2)

                if component == 'X':
                    channel_signal = signal_data[:, x_channel_number]
                elif component == 'Y':
                    channel_signal = signal_data[:, y_channel_number]
                elif component == 'Z':
                    channel_signal = signal_data[:, z_channel_number]
                else:
                    print_message(text='Ошибка чтения номера компоненты. '
                                       'Обработка прервана', level=2)
                    return None

                # расчет спектра сигнала
                spectrum_data = spectrum(signal=channel_signal,
                                         frequency=resample_frequency)

                # расчет энергии сигнала
                energy_value = calc_energy_by_spectrum(
                    spectrum_data=spectrum_data,
                    f_min=f_min_calc, f_max=f_max_calc)

                # запись энергии в массив
                energy_calc_result[component_index, file_index,
                                   interval_number] = energy_value

                print_message(text='Энергия компоненты посчитана', level=2)
    print_message(text='Расчет энергий завершен', level=0)

    print_message(text='Экспорт результатов в файл...', level=0)
    # сборка имен для временных интервалов
    time_interval_names = list()
    for i in range(interval_amount):
        left_interval_edge = left_edge + i * interval_size
        right_interval_edge = left_interval_edge + interval_size
        name = 'Interval_{}-{}'.format(left_interval_edge, right_interval_edge)
        time_interval_names.append(name)

    # сборка данных по точкам (имя точки, координаты)
    points_data = list()
    for point_info in file_statistics.select():
        points_data.append((point_info.point, point_info.x_coord,
                            point_info.y_coord))

    # упаковкак данных в ods-файл
    energy_to_file(components=components, points=points_data,
                   intervals=time_interval_names,
                   data_matrix=energy_calc_result,
                   output_folder=directory_path,
                   output_name='energy_data')
    print_message(text='Экспорт результатов завершен', level=0)
