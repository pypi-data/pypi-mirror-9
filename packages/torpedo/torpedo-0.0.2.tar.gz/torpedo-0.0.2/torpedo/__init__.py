from selenium import webdriver
import requesocks
import time
import subprocess
import shlex

def headless(**kw):
	port = kw.pop('port', 9050)
	phantom = kw.pop('phantom', '/usr/local/bin/phantomjs')

	service_args = [
		'--proxy=127.0.0.1:{}'.format(port),
		'--proxy-type=socks5',
		]
	return webdriver.PhantomJS(phantom, service_args=service_args)

def session(**kw):
	port = kw.pop('port', 9050)
	_session = requesocks.session(**kw)
	_session.proxies = {
		'http': 'socks5://127.0.0.1:{}'.format(port), 
		'https' : 'socks5://127.0.0.{}'.format(port)
	}
	return _session

def get_ip():
	"""
	get your current ip via the proxy
	"""
	s = session() 
	r = s.get('http://icanhazip.com/')
	return r.content.strip()

def refresh_ip():
	"""
	Restart Tor until you get a new ip.
	"""
	ip = get_ip()
	new_ip = ip 
	while ip == new_ip:
		subprocess.Popen(shlex.split('sudo pkill -sighup tor'))
		time.sleep(5)
		new_ip = get_ip()