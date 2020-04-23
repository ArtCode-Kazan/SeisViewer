Данный пакет предназначен для полевой обработки сверочных данных. Пакет
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
    - NumPy         version 1.16.3
    - Matplotlib    version 2.1.2
    - SeisCore      version 0.3.1


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

# version 0.2.1
Добавлены опции выгрузки спектров (сглаженного и несглаженного) сигналов в виде
 файлов, а также опция выгрузки графиков коэф-тов корреляции для каждого файла
 отдельно

# version 0.2.2beta
Добавлена опция выгрузки участка сигнала для строящейся спектрограммы. Изменена
структура ORM - добавлен тип данных (GRP | MSI). Убран тип экспорта в расчете
спектрограмм.
Зависимости: SeisPars 0.1.2, SeisCore 0.0.34sm2ref

# version 0.2.2
Добавлена опция выгрузки участка сигнала для строящейся спектрограммы. Изменена
структура ORM - добавлен тип данных (GRP | MSI). Убран тип экспорта в расчете
спектрограмм. Изменен алгоритм создания БД  - добавлена возможность автозамены
предыдущей БД на пустую новую
Зависимости: SeisPars 0.1.2, SeisCore 0.0.34sm2ref

# version 0.2.3
Добавлена опция - получение статистики по bin-файлам
Зависимости: SeisPars 0.1.2ref, SeisCore 0.0.34sm2ref

# version 0.2.4ref
Все функции изменены с учетом пакета SeisPars vers 0.1.3ref (считывание файлов
на основе класса BinaryFile)
Зависимости: SeisPars 0.1.3, SeisCore 0.0.35sm2ref

# version 0.2.5ref
Добавлен контроль за памятью при считывании выборок сигнала, контроль за
коррекностью файлов
Зависимости: SeisPars 0.1.4, SeisCore 0.0.35sm2ref

# version 0.2.6ref
Добавлена функция для присоединения координат точек из внешнего файла -
JoinCoords. Также добавлена функция для расчета спектральной энергии по точкам.
Исправлена ошибка, связанная с флагом ресемплирования
Зависимости: SeisPars 0.1.6, SeisCore 0.0.36sm2ref

# version 0.2.7
Добавлена функция сшивки bin-файлов в один файл - JoinFiles

# version 0.2.8
Изменена функция расчета энергии с учетом обновления SeisCore
Зависимости: SeisPars 0.1.7, SeisCore 0.0.37sm2ref

# version 0.2.9ref
Пакет исправлен с учетом новых зависимостей:
SeisPars 0.2.5, SeisCore 0.1.4ref

# version 1.0.0
Create GUI application with using PyQt
Requires:  SeisCore 0.2.8

# version 1.0.1
Fix bug: setting time interval in GUI (Revise part)
Requires:  SeisCore 0.3.0

# version 1.0.2
Change algorithm: deprecated time limits for creating spectrograms and
revise processing 
Requires: SeisCore 0.3.1

# version 1.0.3
Add detrending of signal for revise processing 
Requires: SeisCore 0.3.4

# version 1.0.4
Add new option: stitching binary files (for Baikal7)
Add link for SeisCore package
Requires: SeisCore 0.3.7

# version 1.0.5
Fix bug in stitching file algorithm
Requires: SeisCore 0.3.7

# version 1.0.6
Fix bug - migration to SeisCore 0.3.8
Requires: SeisCore 0.3.8

# version 1.0.7
Add new option - spectrogram viewer for seismic signal
Requires: SeisCore 0.3.8

# version 1.1.0
Add new option - spectrogram viewer for seismic signal. Add possibility for
 selection loading file  - from list or from need path 
Requires: SeisCore 0.3.8 

# version 1.1.1
Code refactoring: column "Record type" was removed from main window (don't
 need, 'ZXY' record type setup by default in BinaryFile class)
 Requires: SeisCore 0.3.8 
 
# version 1.1.2
Code refactoring: code refactoring with SeisCore vers. 0.3.9
 Requires: SeisCore 0.3.9
 
# version 1.1.3
SpectrogramViewer was edited: remove Fourier filter (not need) and add
spectrogram coordinate tracing for fixation datetime coordinate
 Requires: SeisCore 0.3.9
 
# version 1.1.4
Code refactoring: code refactoring with SeisCore vers. 0.3.11
 Requires: SeisCore 0.3.11
 
# version 1.1.5
Fix bug in ReviseForm: fix collect binary signal in one array
 Requires: SeisCore 0.3.14
