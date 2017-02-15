import requests
import random
import grequests
import time

if __name__ == '__main__':
	while True:
		rs = (grequests.post('http://127.0.0.1:8888/addtemp', data={'message': random.randint(1,100)}) for u in xrange(0,1000))
		grequests.map(rs)
		time.sleep(5)