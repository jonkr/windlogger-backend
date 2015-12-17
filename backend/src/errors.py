

class AppSpecificError(Exception):

	def __init__(self):
		self.status_code = 500
		self.message = 'An error occurred'

	def format(self):
		return {
			'error': self.__class__.__name__,
			'message': self.message,
			'code': self.status_code
		}

class SensorNotFoundError(AppSpecificError):

	def __init__(self, id_):
		self.message = 'There is (no longer) a sensor with ID={} ' \
		               'available. If you came here via a bookmark, the chart ' \
		               'you are looking for may still be available if you can ' \
		               'locate it in the map view.'.format(id_)
		self.status_code = 404