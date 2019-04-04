import pandas
from directories_manager import create_directory, create_file

class CSVWriterWrapper():
	CSV_DIRECTORY = 'csv_dataset'

	def __init__(self, fieldnames):
		create_directory(self.CSV_DIRECTORY)
		self.fieldnames = fieldnames
		self.filename = './' + self.CSV_DIRECTORY + '/' + 'more_labels_dataset.csv'
		create_file(self.filename, fieldnames)			
		

	def write_line(self, row_dict):
		print(row_dict)
		if list(row_dict.keys()) != self.fieldnames:
			return False
		else:
			with open(self.filename, 'a') as f:
				f.write(','.join([str(x) for x in row_dict.values()]) + '\n')
			print('I am writing!')
			return True
