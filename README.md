﻿Данный пакет предназначен для полевой обработки сверочных данных. Пакет
представляет собой GUI-приложение

Структура пакета:
    - CMDInterface (пакет содержит функции для взаимодействия с интерфейсной
    частью)
        - CorrelationCalc.py - модуль для вычисления коррляций приборов
        - CreateDBase.py    - модуль для создания БД
        - PreAnalysisCalc.py    - модуль для проведения пред анализа
        - SpectrogramCalc.py    - модуль для построения 2D-спектрограмм
    - DBase (пакет содержит модули для работы с БД)
        - SqliteDBase.py     - модуль с классом управления ORM-моделью
    - Functions (пакет содержит вспомогательные функции)
        - Exporting.py  - модуль для экспорта результатов в виде текстовых
        файлов
        - Plotting.py   - модуль для экспорта результатов в виде png-картинок
        - Processing.py - модуль со вспомогательными функциями


# Необходимые модули
    - Matplotlib    version 2.1.2
    - SeisPars      version 0.1.1
    - SeisCore      version 0.0.32sm2


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

# version 0.1.3
Убрана завязка пакета json файл, теперь программа работает с SQLite БД.

# version 0.1.4
Добавлена операция проведения предварительного анализа сигнала. Убрана
зависимость на PyQt и json

# version 0.2.0
Пересобран код, отдельные функции собраны в блоки-модули, создан класс для
управления БД сессии
Зависимости: SeisPars 0.1.1, SeisCore 0.0.32sm2

# version 0.2.1ref
Код изменен в соответствии с SeisPars 0.1.1ref
Добавлена опция построения графиков коэф-тов корреляции для каждого прибора в
отдельности
Зависимости: SeisCore 0.0.34sm2ref, SeisPars 0.1.1ref