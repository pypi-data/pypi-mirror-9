import os

class Target(object):

	def ready(self):
		raise NotImplementedError('You need to define exists().')


class FileTarget(object):

	def __init__(self.py, path, namespace=''):
		self.path = path

	def ready(self):
		return os.path.isfile(self.path)






