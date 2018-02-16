import re

s='BinData-sss'


if re.match('[a-zA-Z0-9-_]*$',s):
    print('Ok')
else:
    print('None')

