import os

directory_path=r'D:\AppsBuilding\TestingData\BinData'

bin_files_list = list()
folder_struct = os.walk(directory_path)
for root_folder, folders, files in folder_struct:
    for file in files:
        name, extention = file.split('.')
        # поиск bin-файла
        if extention in ['00', 'xx']:
            # получение полного пути к bin-файлу
            bin_file_path = os.path.join(root_folder, file)
            bin_files_list.append(bin_file_path)

print(bin_files_list)


