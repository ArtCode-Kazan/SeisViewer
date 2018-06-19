from datetime import datetime

dev_start = datetime(2018, 4, 15, 0, 0, 5)
start_grp = datetime(2018, 4, 15, 21, 44, 17)

c = (start_grp - dev_start).total_seconds()
print(c)
