from task import Task
from resource import Resource

def as_list(item):
	if isinstance(item, dict):
		return item.values()

	if hasattr(item, '__iter__'):
		return list(item)

	return [item]


class RunnerException(Exception):
	pass


class Runner(Task):

	# The null runner has no tasks, but is valid
	tasks = {}
	layout = {
		'END':[]
	}
	until = None
	lot = None

	def check_layout(self):
		# ensure that all tasks in layout are defined in tasks
		laid_out_tasks = set([t for t in self.layout if t is not 'END'])

		missing = [
			t for t in self.layout 
			if t not in self.tasks and t is not 'END'
		]
		if len(missing)>0:
			raise RunnerException(
				'The following tasks were defined in the layout, but are '
				'not defined in the tasks: %s' % ', '.join(missing)
			)

		unused = [t for t in self.tasks if t not in self.layout]
		if len(missing)>0:
			raise RunnerException(
				'Warning, the following tasks are defined, but not included '
				'in the layout (they will never be run): %s'
				% ', '.join(unused)
			)



	def resolve_lot(self, lot=None):

		# either lot must be in class definition or passed at run time.
		if lot is None and self.lot is None:
			raise RunnerException('the lot could not be resolved')

		# if only one is defined, use it
		if lot is None or self.lot is None:
			return lot or self.lot
		
		# if both are defined, and aren't equal, concatenate them
		if self.lot != lot:
			return lot + '.' + self.lot

		# otherwise they're identical, so don't concatenate
		return lot



	def get_ready(self, lot, as_pilot=False):

		self.as_pilot = as_pilot

		# get all the tasks ready
		for task in self.tasks.values():
			task.get_ready(lot, as_pilot)


	def recursively_schedule(self, task_names):
		'''
			accepts the name of a task, or an iterable thereof, and schedules
			those which are not yet done.
		'''
		task_names = as_list(task_names)
		scheduled = []
		for task_name in reversed(task_names):

			# if the task isn't done, schedule it and its dependencies
			if not self.tasks[task_name].exists():
				scheduled.append(task_name)

				# schedule dependant jobs, if any
				try:
					scheduled.extend(
						self.recursively_schedule(self.layout[task_name])
					)
				except KeyError:
					pass
				
		return scheduled


	def _run(self, lot=None, as_pilot=False, until=None):
		self.lot = self.resolve_lot(lot)
		self.run(as_pilot=as_pilot, until=until)


	def run(self, as_pilot=False, until=None):

		self.as_pilot = as_pilot
		self.get_ready(self.lot, as_pilot)

		# ensure that self.lot is defined and is string-like
		try:
			self.lot = str(self.lot)
		except AttributeError:
			raise RunnerException('You must specify a lot for your runner')

		# make sure that all the tasks are well-defined and actually get used
		self.check_layout()

		print 'Starting runner for lot %s.' % self.lot

		# by default, run whatever is in 'END'
		until = until or self.until
		if until is None:
			until = self.layout['END']

		schedule = self.recursively_schedule(until)

		# completely run the until_tasks
		while len(schedule) > 0:
			next_task_name = schedule.pop()
			print ' - running %s.' % next_task_name
			self.tasks[next_task_name]._run(self.lot, self.as_pilot)



