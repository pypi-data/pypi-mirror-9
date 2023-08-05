# -*- coding: utf-8 -*-
import time, logging, logging.handlers, json, sys, inspect

class LogPrint(object):
	"""
	Classe de BackOffice para gerenciar output e logs.
	b = Logprint(echo=True,logfile="log.txt",loglevel="DEBUG")

	Parameters		Default/Other
	echo			True/False
	logfile			File/None
	loglevel		DEBUG/INFO/WARNING/ERROR
	logformat		See logging doc
	logsize			50000000/in Bytes
	backupCount		3/# of files
	"""
	levels = {
		'CRITICAL'	: 50,
		'ERROR' 	: 40,
		'WARNING'	: 30,
		'INFO'		: 20,
		'DEBUG'		: 10
	}
	def __init__(self,echo=True,logfile=None,loglevel='INFO',logformat='[%(asctime)s] %(filename)s:%(levelname)s: %(message)s',logsize=50000000,backupCount=3):
		self.echo = echo
		self.logfile = logfile
		self.logsize = logsize
		self.loglevel = loglevel
		self.backupCount = backupCount
		if ( self.logfile ):
			logging.basicConfig(filename=self.logfile,level=loglevel,format=logformat,
				datefmt='%Y-%m-%d %H:%M:%S')
			self.logger = logging.getLogger('generic')
			handler = logging.handlers.RotatingFileHandler(self.logfile, maxBytes=self.logsize, backupCount=self.backupCount)
			self.logger.addHandler(handler)

	def critical(self,msg,code=1):
		"""
		Args: msg="menssagem", code="codigo de saida"
		Se definido, exibe a mensagem
		Se definido, salva no log
		e entao aborta
		"""
		msg = "%s: %s" % (inspect.stack()[1][3],msg)
		if ( self.echo ):
			sys.stderr.write('%s[%s] CRITICAL: %s%s\n' % (Bcolors.MAGENTA, self.get_time(), msg, Bcolors.ENDC))
		if ( self.logfile ):
			self.logger.error(msg)
		sys.exit(code)

	def error(self,msg):
		"""
		Args: msg="menssagem"
		Se definido, exibe a mensagem
		Se definido, salva no log
		"""
		msg = "%s: %s" % (inspect.stack()[1][3],msg)
		if ( self.echo ):
			sys.stderr.write('%s[%s] ERROR: %s%s\n' % (Bcolors.FAIL, self.get_time(), msg, Bcolors.ENDC))
		if ( self.logfile ):
			self.logger.error(msg)

	def warning(self,msg):
		"""
		Args: msg="menssagem"
		Se definido, exibe a mensagem
		Se definido, salva no log
		"""
		msg = "%s: %s" % (inspect.stack()[1][3],msg)
		if ( (self.echo) and (self.levels['WARNING'] >= self.levels[self.loglevel]) ):
			print Bcolors.WARNING + "[%s] warning: %s" % (self.get_time(), msg) + Bcolors.ENDC
		if ( self.logfile ):
		 	self.logger.warning(msg)

	def info(self,msg):
		"""
		Args: msg="menssagem"
		Se definido, exibe a mensagem
		Se definido, salva no log
		"""
		msg = "%s: %s" % (inspect.stack()[1][3],msg)
		if ( (self.echo) and (self.levels['INFO'] >= self.levels[self.loglevel]) ):
			print Bcolors.OKBLUE + "[%s] info: %s" % (self.get_time(), msg) + Bcolors.ENDC
		if ( self.logfile ):
			self.logger.info(msg)

	def debug(self,msg):
		"""
		Args: msg="menssagem"
		Se definido, exibe a mensagem
		Se definido, salva no log
		"""
		msg = "%s: %s" % (inspect.stack()[1][3],msg)
		if ( (self.echo) and (self.levels['DEBUG'] >= self.levels[self.loglevel]) ):
			sys.stderr.write('%s[%s] debug: %s%s\n' % (Bcolors.OKGREEN, self.get_time(), msg, Bcolors.ENDC))
		if ( self.logfile ):
			self.logger.debug(msg)

	def get_time(self):
		"""
		Args: none
		Retorna a data no formato YYYY-MM-DD HH:MM:SS
		"""
		return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

	def print_json(self,json_in):
		"""
		Args: json
		Exibe seu json em formato legivel
		"""
		self.debug("\n" + json.dumps(json_in, sort_keys=True, indent=4, separators=(',', ': ')))

class Bcolors:
	"""
	Fornece cores para exibir mensagens no terminal
	"""
	HEADER = '\033[95m'
	OKBLUE = '\033[36m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	MAGENTA = '\033[45m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'

	def disable(self):
		"""
		Apaga as novas definicoes de cor do terminal
		"""
		self.HEADER = ''
		self.OKBLUE = ''
		self.OKGREEN = ''
		self.WARNING = ''
		self.MAGENTA = ''
		self.FAIL = ''
		self.ENDC = ''
