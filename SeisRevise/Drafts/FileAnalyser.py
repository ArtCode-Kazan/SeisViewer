from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.Functions.Filter import band_pass_filter
from SeisCore.Functions.Spectrogram import create_spectrogram
from SeisCore.Plotting.Plotting import plot_signal
import datetime
import os
import numpy as np

root=r'/media/michael/Seagate Backup Plus Drive/Yamburg/FieldData/Well_3047/src/3047_10-14'
files=['YM_011_K06_2019-11-29_11-16-13.xx',
       'YM_013_SigmaN001_2019-11-29_07-59-08.bin']

read_limits=[(datetime.datetime(2019,11,29,13),
              datetime.datetime(2019,11,29,13,30))]

output_folder=r'/home/michael/Temp/Signals'

# read_dt_start=datetime.datetime(2019,12,5,14)
# read_dt_stop=datetime.datetime(2019,12,5,14,10)

bandpass_filter_limits=(0,0.4)
bandpass_step=0.1
spectrograms_freq_limits=(0,250)

for file in files:
    file_path = os.path.join(root, file)
    bin_data = BinaryFile()
    bin_data.path = file_path
    bin_data.use_avg_values = False
    for dt_lims in read_limits:
        bin_data.read_date_time_start=dt_lims[0]
        bin_data.read_date_time_stop=dt_lims[1]
        signal=bin_data.signals[:,0]

        file_name=os.path.basename(file_path).split('.')[0]

        for band_f_min in np.arange(bandpass_filter_limits[0],
                                    bandpass_filter_limits[1], bandpass_step):
            # band_f_max=band_f_min+bandpass_step
            band_f_max=500

            exp_folder_name=f'{band_f_min}-{band_f_max}_Hz'
            date_interval_template=f'{dt_lims[0].strftime("%Y-%m-%d-%H-%M-%S")}_' \
                                   f'{dt_lims[1].strftime("%Y-%m-%d-%H-%M-%S")}'

            exp_path=os.path.join(output_folder, file_name, date_interval_template,
                                  exp_folder_name)
            if not os.path.exists(exp_path):
                os.makedirs(exp_path)

            filter_signal=band_pass_filter(signal=signal,
                                           frequency=bin_data.signal_frequency,
                                           f_min=band_f_min, f_max=band_f_max)

            plot_signal(0,bin_data.signal_frequency, filter_signal, 'Filtered '
                                                                    'signal',
                        exp_path, 'FilteredSignal')

            create_spectrogram(filter_signal, bin_data.signal_frequency, exp_path,
                               'SpectrogramData', spectrograms_freq_limits[0],
                               spectrograms_freq_limits[1])
    print(f'file {file} done')






