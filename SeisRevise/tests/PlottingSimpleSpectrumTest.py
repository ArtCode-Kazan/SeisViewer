from SeisPars.Parsers.BinarySeisReader import read_seismic_file_baikal8 as rsf
from SeisRevise.Functions.PlottingSimpleSpectrum import simple_spectrum

filepath = r'D:\AppsBuilding\TestingData\TestHydroFrac\BinFiles' \
          r'\9_2015_12_06_04_00_21_B8_00_ca0069.xx'


signal = rsf(file_path=filepath, signal_frequency=1000, only_signal=True,\
           resample_frequency=250, start_moment=0, end_moment=10000)[:,0]
simple_spectrum(signal=signal,frequency=250,median_filter_parameter=3,
                marmett_filter_parameter=7,f_min=0,f_max=10,
                output_folder=r'D:/TEMP',output_name='qwerty')
