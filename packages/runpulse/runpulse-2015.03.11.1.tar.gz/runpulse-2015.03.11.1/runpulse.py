#!/usr/bin/python

import sys
import time
import os
import argparse

def parse_args(argv):
	parser = argparse.ArgumentParser(description="%s - continuous periodic execution of a command" % sys.argv[0])
	parser.add_argument('-p', '--period', required=True, dest='period', type=int, help='period in seconds')
	parser.add_argument('-c', '--command', required=True, dest='command', type=str, help='command to execute')
	args = parser.parse_args(argv)
	return args

def main():
	args = parse_args(sys.argv[1:])
	next_time = time.time()
	while True:
		if time.time() >= next_time:
			os.system(args.command)
			next_time = (int(time.time())/args.period+1)*args.period
		else:
			try:
				time.sleep(1)
			except:
				break

if __name__ == '__main__':
	main()
