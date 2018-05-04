﻿Данный пакет предназначен для полевой обработки сверочных данных. Пакет
представляет собой GUI-приложение

Структура пакета:
    - Functions (пакет содержит функции для вычисления)
        - CorrelationToFile.py    - модуль для записи матрицы коэф-тов
        корреляции в файл
        - CrossCorrelate.py       - модуль для вычисления коэффициентов
        корреляции между столбцами массивов амплитуд спектров
        - ExportFolder.py         - модуль для генерации пути папки экспорта
        результатов расчета
        - PlottingAllSpectrums.py - модуль для построения плота со всеми
        сглаженными спектрами всех bin-файлов
        - PlottingCorrelation.py  - модуль для отрисовки графиков корреляции
        спектров для кадой пары приборов
        - PlottingSignal.py       - модуль для построения графика сигнала
        - PlottingSpectrogram.py  - модуль для построения 2D спектрограммы
        в виде картинки
        - PlottingSpectrum.py     - модуль для отрисовки исходного и
        сглаженного кумулятивных спектров сигнала
        - WriteSelectionSignal.py - модуль для записи сигнала в файл
    - Interface (пакет содержит реализацию QT-интерфейса)
        - QTForms (подпакет содержит QT данные формы и ее конвертацию в python)
            - ConversionString.cmd - строка для конвертации ui в py
            - MainForm.py   - GUI описание в python
            - MainForm.ui   - QT-интерфейс
        - MainForm.py       - основная часть программы

# Необходимые модули
    - PyQT5         version 5.10
    - Matplotlib    version 2.1.2
    - SeisPars      version 0.1.0
    - SeisCore      version 0.0.23


# version 0.0.0
Первая версия пакета

# version 0.0.1
Предварительно дописана часть, связанная с генерацией 2D-спектрограмм

# version 0.0.2
Сделаны небольшие правки в модуле PlottingSpectrogram

# version 0.0.3
Проект в разработке.

# version 0.0.4
Предварительная версия пакета готова

# version 0.0.5
Исправлена ошибка вылета программ в случае, если неверно указаны параметры
построения 2D спектрограммы. Добавлена возможность выбора типа структуры папок
для экспорта. написана функция генерации пути к папке для экспорта результатов

# version 0.0.6
Изменен интерфейс - сделан ListBox для выбора типа записи в обеих вкладках

# version 0.0.7
Исправлена ошибка, возникающая при неверно названной папки сверки. Тперь
ведется проверка имен папок на правильность (допустима латиница, цифры, тире и
нижнее подчеркивание)

# version 0.0.8
Раскоментирован код выполнения процедуры построения 2D спектрограмм. В версии
0.0.7 забыл его раскомментировать

# version 0.0.9
Добавлен контроль за именем папок и структурой папок и файлов внутри них в
разделе расчет коэф-тов корреляций (вторая вкладка формы)

# version 0.0.10
Добавлено описание в README.md. Изменен алгоритм запуска GUI

# version 0.0.11
Исправлена ошибка запуска GUI

# version 0.0.12
Оптимизирован алгоритм, переработан GUI дизайн приложения, справлены ошибки.
Зависимости: SeisPars 0.0.16, SeisCore 0.0.22

# version 0.1.0
Исправлены мелкие ошибки
Зависимости: SeisPars 0.1.0, SeisCore 0.0.23

# version 0.1.1
Исправлен GUI-интерфейс - расширен частотный диапазон для анализа и отрисовки
спектров и спектрограмм

# version 0.1.2b
Добавлена тестовая реализация консольной версии интерфейса. Пока в стадии
тестирования

# version 0.1.2
Завершена реализация консольной версии интерфейса. Пакет готов к интеграции с
GUI интерфейсом на Lazarus