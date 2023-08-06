


class CilenisValidationException(Exception):
	
	def __init__(self, msg=None, help=None):
		self.__msg  = msg  or None
		self.__help = help or None
	
	def __str__(self):
		msg  = self.__msg  or "CilenisValidationException general error"
		msg += "\n\t\_ %s" % self.__help if self.__help else ""
		return msg

class CilenisApiException(Exception):
	
	def __init__(self, msg=None, help=None):
		self.__msg  = msg  or None
		self.__help = help or None
	
	def __str__(self):
		msg  = self.__msg  or "CilenisApiException general error"
		msg += "\n\t\_ %s" % self.__help if self.__help else ""
		return msg