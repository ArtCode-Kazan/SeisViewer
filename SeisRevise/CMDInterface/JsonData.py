import sys
import os
import json

from SeisCore.GeneralFunction.cmdLogging import error_format


def check_node(dic, key_name, value_type):
    """
    Функция для проверки узла Json-файла
    :param dic: словарь json-файла
    :param key_name: имя ключа
    :param value_type: тип или типы значений
    :return: True-если все в порядке, False-если найдены ошибки
    """
    if key_name not in dic.keys():
        text = 'Ключ {} не найден'.format(key_name)
        error_text = error_format(number=1, text=text)
        print(error_text)
        return False
    value = dic[key_name]
    if not isinstance(value, value_type):
        text = 'Неверный тип ключа {}: ' \
               'expect {},  reality {}'.format(key_name, value_type,
                                               type(value))
        error_text = error_format(number=2, text=text)
        print(error_text)
        return False
    return True


def create_json():
    """
    Функция для создания пустого Json-файла с требуемой структурой
    :return: void
    """
    parameters = sys.argv
    if len(parameters) != 2:
        error_text = error_format(number=3,
                                  text='Неверное число параметров')
        print(error_text)
        return None

    folder_path = parameters[1]
    # folder_path = r'D:\temp'
    if not os.path.exists(folder_path):
        error_text = error_format(number=4,
                                  text='Не найдена папка для сохранения json')
        print(error_text)
        return None

    # итоговый словарь
    json_structure = dict()

    # общие данные для обработки
    gen_data = json_structure['general_data'] = dict()
    # путь к рабочей папке с данными
    gen_data['directory_path'] = 'C:\\'
    # тип файлов
    gen_data['file_type'] = 'Baikal7'
    # тип записи
    gen_data['record_type'] = 'XYZ'
    # частота записи сигнала
    gen_data['signal_frequency'] = 250
    # частота ресемплирования
    gen_data['resample_frequency'] = 250
    # необходимость ресемплирования (True - без ресемплирования, False - с
    # ресемплированием)
    gen_data['is_no_resample'] = True
    # список компонент для анализа
    gen_data['x_component'] = True
    gen_data['y_component'] = True
    gen_data['z_component'] = True

    # данные для построения 2D-спектрограмм
    spectrograms = json_structure['spectrograms'] = dict()
    # размер временного интервала (часы)
    spectrograms['time_interval'] = 1
    # размер окна расчета (отсчтты)
    spectrograms['window_size'] = 8192
    # размер сдвига окна (отсчеты)
    spectrograms['noverlap_size'] = 256
    # минимальная частота для визуализации (Гц)
    spectrograms['min_frequency'] = 1
    # максимальная частота для визуализации (Гц)
    spectrograms['max_frequency'] = 20
    # тип структуры экспорта результатов
    spectrograms['export_folder_structure'] = 'HourStructure'

    # данные для вычисления корреляционных характеристик приборов
    correlation = json_structure['correlation'] = dict()
    # левая граница выборки сигнала (секунда)
    correlation['left_edge'] = 600
    # правая граница выборки сигнала (секунда)
    correlation['right_edge'] = 1200
    # размер окна расчета корреляций (отсчеты)
    correlation['window_size'] = 8192
    # размер сдвига окна (отсчеты)
    correlation['noverlap_size'] = 4096
    # параметр медианного фильтра
    correlation['median_filter'] = 7
    # использование медианного фильтра
    correlation['median_using'] = True
    # параметр фильтра marmett
    correlation['marmett_filter'] = 7
    # использование фильтра marmett
    correlation['marmett_using'] = True
    # минимальная частота для расчетов (Гц)
    correlation['f_min_calc'] = 1
    # максимальная частота для расчетов (Гц)
    correlation['f_max_calc'] = 10
    # минимальная частота для визуализации (Гц)
    correlation['f_min_vizual'] = 1
    # максимальная частота для визуализации (Гц)
    correlation['f_max_vizual'] = 10

    # файлы для экспорта
    correlation['selection_signal_to_file'] = False
    correlation['selection_signal_to_graph'] = False
    correlation['spectors_for_each_device'] = False
    correlation['general_spector'] = False
    correlation['correlation_matrix_to_file'] = False
    correlation['correlation_matrix_to_graph'] = False

    # генерация пути к выходному файлу
    output_file = os.path.join(folder_path, 'session.json')
    # запись файла
    try:
        with open(output_file, 'w', encoding='utf8') as json_file:
            lines = json.dumps(obj=json_structure,
                               indent=4,
                               separators=(',', ': '),
                               ensure_ascii=False)
            json_file.write(lines)
    except FileExistsError:
        error_text = error_format(number=5,
                                  text='Ошибка сохранения json')
        print(error_text)


def checking_json(file_path, checking_node='general_data'):
    """
    Функция для проверки json-файла
    :param file_path: путь к файлу
    :param checking_node: имя узла для проверки
    :return: True/False
    """
    if not os.path.exists(file_path):
        print('Не найден файл JSON')
        return False

    # проба парсинга файла
    try:
        json_data = json.load(open(file_path, 'r'))
    except ValueError:
        print('Ошибка чтения json')
        return False

    # получение списка узлов первого порядка
    main_nodes = json_data.keys()

    # проверка узла с общими данными
    if checking_node == 'general_data':
        if 'general_data' not in main_nodes:
            print('Узел с общими данными отсутствует')
            return False

        general_data = json_data['general_data']

        # проверка пути к рабочей папке
        if not check_node(dic=general_data,
                          key_name='directory_path',
                          value_type=str):
            return False
        value = general_data['directory_path']
        if not os.path.isdir(value):
            print('Путь к рабочей папке не существует')
            return False

        # проверка типа файла
        if not check_node(dic=general_data,
                          key_name='file_type',
                          value_type=str):
            return False
        value = general_data['file_type']
        if value not in ['Baikal7', 'Baikal8']:
            print('Неверно указан тип файла')
            return None

        # тип записи
        if not check_node(dic=general_data,
                          key_name='record_type',
                          value_type=str):
            return False
        value = general_data['record_type']
        if value not in ['ZXY', 'XYZ']:
            print('Неверно указан тип записи')
            return False

        # частота записи сигнала
        if not check_node(dic=general_data,
                          key_name='signal_frequency',
                          value_type=int):
            return False

        # частота ресемплирования
        if not check_node(dic=general_data,
                          key_name='resample_frequency',
                          value_type=int):
            return False

        # проверка кратности частот ресемплирования и исходной частоты
        if general_data['signal_frequency'] % \
                general_data['resample_frequency'] != 0:
            text = error_format(number=3,
                                text='Исходная частота должнв быть кратна '
                                     'частоте ресемплирования')
            print(text)
            return False

        # список компонент для анализа
        if not check_node(dic=general_data,
                          key_name='x_component',
                          value_type=bool):
            return False
        if not check_node(dic=general_data,
                          key_name='y_component',
                          value_type=bool):
            return False
        if not check_node(dic=general_data,
                          key_name='z_component',
                          value_type=bool):
            return False

        if not (general_data['x_component'] or general_data['y_component'] or
                general_data['z_component']):
            print('Не выбрано ни одной компоненты для анализа')
            return False
        return True

    # проверка узла с данными для построения спектрограмм
    if checking_node == 'spectrograms':
        if 'spectrograms' not in main_nodes:
            print('Узел с данными для построения 2D-спектрограмм не найден')
            return False

        spectrograms_parameteres = json_data['spectrograms']

        # размер временного интервала (часы)
        if not check_node(dic=spectrograms_parameteres,
                          key_name='time_interval',
                          value_type=(int, float)):
            return False

        # размер окна расчета (отсчeты)
        if not check_node(dic=spectrograms_parameteres,
                          key_name='window_size',
                          value_type=int):
            return False

        # размер сдвига окна (отсчеты)
        if not check_node(dic=spectrograms_parameteres,
                          key_name='noverlap_size',
                          value_type=int):
            return False

        # минимальная частота для визуализации (Гц)
        if not check_node(dic=spectrograms_parameteres,
                          key_name='min_frequency',
                          value_type=(int, float)):
            return False

        # максимальная частота для визуализации (Гц)
        if not check_node(dic=spectrograms_parameteres,
                          key_name='max_frequency',
                          value_type=(int, float)):
            return False

        # проверка частот на правильность указания
        if spectrograms_parameteres['min_frequency'] >= \
                spectrograms_parameteres['max_frequency']:
            text = 'Неверно указан диапазон частот визуализации спектрограмм'
            error_text = error_format(number=4, text=text)
            print(error_text)
            return False

        # тип структуры экспорта результатов
        if not check_node(dic=spectrograms_parameteres,
                          key_name='export_folder_structure',
                          value_type=str):
            return False
        value = spectrograms_parameteres['export_folder_structure']
        if value not in ['HourStructure', 'DeviceStructure']:
            print('Неверно указана структура экспорта результатов')
            return False
        return True

    # проверка узла с данными для расчета корреляций
    if checking_node == 'correlation':
        if 'correlation' not in main_nodes:
            print('Узел с данными для расчета корреляций не найден')
            return False

        correlation_parameters = json_data['correlation']

        # левая граница выборки сигнала (секунда)
        if not check_node(dic=correlation_parameters,
                          key_name='left_edge',
                          value_type=int):
            return False

        # правая граница выборки сигнала (секунда)
        if not check_node(dic=correlation_parameters,
                          key_name='right_edge',
                          value_type=int):
            return False

        # проверка на правильность указания границ чистого участка
        if correlation_parameters['left_edge'] >= \
                correlation_parameters['right_edge']:
            error_text = error_format(number=5, text='Неверно указан диапазон '
                                                     'чистого сигнала')
            print(error_text)
            return False

        # размер окна расчета корреляций (отсчеты)
        if not check_node(dic=correlation_parameters,
                          key_name='window_size',
                          value_type=int):
            return False

        # размер сдвига окна (отсчеты)
        if not check_node(dic=correlation_parameters,
                          key_name='noverlap_size',
                          value_type=int):
            return False

        # параметр медианного фильтра
        if not check_node(dic=correlation_parameters,
                          key_name='median_filter',
                          value_type=int):
            return False

        # проверка, что параметр медианного фильтра нечетный
        if correlation_parameters['median_filter'] is \
                not None and correlation_parameters['median_filter'] % 2 == 0:
            print('Параметр медианного фильтра должен быть нечетным')
            return False

        # параметр фильтра marmett
        if not check_node(dic=correlation_parameters,
                          key_name='marmett_filter',
                          value_type=int):
            return False

        # проверка, что указан хотя бы один параметр фильтрации
        if not (correlation_parameters['marmett_using'] or
                correlation_parameters['median_using']):
            print('Не указан ни один из параметров фильтрации')
            return False

        # минимальная частота для расчетов (Гц)
        if not check_node(dic=correlation_parameters,
                          key_name='f_min_calc',
                          value_type=(int, float)):
            return False

        # максимальная частота для расчетов (Гц)
        if not check_node(dic=correlation_parameters,
                          key_name='f_max_calc',
                          value_type=(int, float)):
            return False

        # проверка пределов частот для расчета
        if correlation_parameters['f_min_calc'] >= \
                correlation_parameters['f_max_calc']:
            print('Неверно указан пределы частот для анализа')
            return False

        # минимальная частота для визуализации (Гц)
        if not check_node(dic=correlation_parameters,
                          key_name='f_min_vizual',
                          value_type=float):
            return False

        # максимальная частота для визуализации (Гц)
        if not check_node(dic=correlation_parameters,
                          key_name='f_max_vizual',
                          value_type=(int, float)):
            return False

        # проверка пределов частот для визуализации
        if correlation_parameters['f_min_vizual'] >= \
                correlation_parameters['f_max_vizual']:
            print('Неверно указан пределы частот для визуализации')
            return False

        # файлы для экспорта
        # выборка сигнала в файл
        if not check_node(dic=correlation_parameters,
                          key_name='selection_signal_to_file',
                          value_type=bool):
            return False

        # выборка сигнала в виде графика
        if not check_node(dic=correlation_parameters,
                          key_name='selection_signal_to_graph',
                          value_type=bool):
            return False

        # спектры по каждому прибору
        if not check_node(dic=correlation_parameters,
                          key_name='spectors_for_each_device',
                          value_type=bool):
            return False

        # график с совмещенными сглаженными спектрами по всем приборам
        if not check_node(dic=correlation_parameters,
                          key_name='general_spector',
                          value_type=bool):
            return False

        # матрица коэф-тов корреляций в виде файла
        if not check_node(dic=correlation_parameters,
                          key_name='correlation_matrix_to_file',
                          value_type=bool):
            return False

        # матрица коэф-тов корреляций в виде графика
        if not check_node(dic=correlation_parameters,
                          key_name='correlation_matrix_to_graph',
                          value_type=bool):
            return False

        # проверка, что хотя бы один из файлов экспорта выбран
        checking = correlation_parameters['selection_signal_to_file'] or \
            correlation_parameters['selection_signal_to_graph'] or \
            correlation_parameters['spectors_for_each_device'] or \
            correlation_parameters['general_spector'] or \
            correlation_parameters['correlation_matrix_to_file'] or \
            correlation_parameters['correlation_matrix_to_graph']
        if not checking:
            print("Не выборан ни один из способов экспорта результатов "
                  "данных по расчетам корреляций")
            return False
        return True
