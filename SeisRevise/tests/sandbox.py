from SeisRevise.Functions.Exporting import energy_to_file



energy_to_file(components=('X','Z'),
               points=(('1',3,4), ('2',5,6), ('5',8,9)),
               intervals=('t1','t2'),
               data_matrix='fah',
               output_folder=r'D:\temp',
               output_name='qwerty')