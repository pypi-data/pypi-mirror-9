from run import Runner 
from task import Task
from resource import Resource, FileResource

DATA_ROOT = '../data'

class Count(Task):

	outputs = FileResource(DATA_ROOT, 'count.txt')
	inputs = None

	def run(self):
		fh = self.outputs.open('w')
		some_numbers_to_write = '\n'.join([str(i) for i in range(10)]) + '\n'
		fh.write(some_numbers_to_write)
		fh.close()

class Greet(Task):


class MyRun(Runner):

	lot = 'my_first_run'

	tasks = {
		'count': Count(),
		#greet: Greet(),
		#merge: Merge(),
		#reverse: Reverse(),
		#last: Last()
	}

	layout = {
		'END': 'count'
		#'END': 'last',
		#'last': 'reverse',
		#'reverse': 'merge',
		#'merge': ['count', 'greet']
	}


if __name__ == '__main__':
	my_runner = MyRun()
	my_runner._run()
