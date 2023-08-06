from utils.database import Session

class SQLAlchemyMiddleware(object):
	def process_request(self, request):
		request.djhcup_session = Session()

	def process_response(self, request, response):
		try:
			session = request.djhcup_session
		except AttributeError:
			return response
		try:
			session.commit()
		except:
			session.rollback()
			raise

	def process_exception(self, request, exception):
		try:
			session = request.djhcup_session
		except AttributeError:
			return
		session.rollback()