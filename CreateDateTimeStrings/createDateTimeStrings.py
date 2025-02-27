from datetime import datetime

YEAR_NUMBER = 2025
MONTH_NUMBER = 3

for day in range(20,24):
	for hour in range(8,24):
		print(f'{datetime(YEAR_NUMBER, MONTH_NUMBER, day, hour, 0, 0, 0).strftime("%m/%d @ %I:%M %p")}')
	print('\n')