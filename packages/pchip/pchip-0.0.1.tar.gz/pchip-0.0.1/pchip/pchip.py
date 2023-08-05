import sys
import pythonwhois
import threading
import logging

array=[
	'.com',
	'.org',
	'.net',
	'.co',
	'.name',
	'.biz',
	'.info',
	'.io',
	'.ca',
	'.eu',
	'.jp',
	'.ru',
	'.us'	
]

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def make_green(ip):
	return '\x1b[32m' + ip + '\033[0m'
def make_red(ip):
	return '\x1b[31m' + ip + '\033[0m'

def main(argv):
	threads = []
	i = 0
	for id in argv:
		for tld in array:
			t = threading.Thread(target=check, args=(id+tld,))
			threads.append(t)
			t.start()
	pass

def check(name):
	try:
		data = pythonwhois.get_whois(name)
		if 'expiration_date' in data:
			logger.info('%-20s %s',name, make_red(u'\u00F8'))
		else:
			logger.info('%-20s %s',name, make_green(u'\u0298'))
	except Exception as e:
		logger.info('%-20s %s',name, make_red(u'\u00F8'))
		pass

#if __name__ == '__main__':
#	sys.exit(main(sys.argv[1:]))
