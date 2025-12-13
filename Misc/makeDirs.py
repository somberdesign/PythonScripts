from os import mkdir
from os.path import isdir, join
from datetime import date, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

i = 0
start_date = date(2026, 2, 1)
end_date = date(2026, 4, 30)
for single_date in daterange(start_date, end_date + timedelta(days=1)):

    i += 1
    if i > 1000:
        print('This thing is out of control! Breaking out of loop.')
        break

    month_dir = single_date.strftime("%Y-%m")
    if not isdir(month_dir):
        mkdir(month_dir)
    mkdir(join(month_dir, single_date.strftime("%Y-%m-%d-%a")))
	

	
