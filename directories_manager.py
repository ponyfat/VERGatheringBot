import os

# ADD ABSOLUTE PASS!

def create_directory(name):
	if not os.path.isdir('./' + name):
		os.mkdir(name)

def create_file(name, fieldnames):
	if not os.path.exists(name):
		with open(name, 'w'):
			pass
		with open(name, 'a') as f:
			f.write(','.join(fieldnames) + '\n')
