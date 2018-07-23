import os

a='cmd.exe /c python -c "{}"'.format('print(\'Hello!\')')
print(a)
os.popen(a)