# -*- coding: utf-8 -*-

from __future__ import print_function

import time
import socket
import datetime
import argparse
import sys

from jaraco import timing

def client_host(server_host):
	"""Return the host on which a client can connect to the given listener."""
	if server_host == '0.0.0.0':
		# 0.0.0.0 is INADDR_ANY, which should answer on localhost.
		return '127.0.0.1'
	if server_host in ('::', '::0', '::0.0.0.0'):
		# :: is IN6ADDR_ANY, which should answer on localhost.
		# ::0 and ::0.0.0.0 are non-canonical but common
		# ways to write IN6ADDR_ANY.
		return '::1'
	return server_host


def _check_port(host, port, timeout=1.0):
	"""
	Raise an error if the given port is not free on the given host.
	"""
	if not host:
		raise ValueError("Host values of '' or None are not allowed.")
	host = client_host(host)
	port = int(port)

	# AF_INET or AF_INET6 socket
	# Get the correct address family for host (allows IPv6 addresses)
	try:
		info = socket.getaddrinfo(host, port, socket.AF_UNSPEC,
			socket.SOCK_STREAM)
	except socket.gaierror:
		if ':' in host:
			info = [(
				socket.AF_INET6, socket.SOCK_STREAM, 0, "", (host, port, 0, 0)
			)]
		else:
			info = [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (host, port))]

	for res in info:
		af, socktype, proto, canonname, sa = res
		s = None
		try:
			s = socket.socket(af, socktype, proto)
			# important that a small timeout is set here to allow the check
			#  to fail fast.
			s.settimeout(timeout)
			s.connect((host, port))
			s.close()
		except socket.error:
			if s:
				s.close()
		else:
			tmpl = "Port {port} is in use on {host}."
			raise IOError(tmpl.format(**locals()))


class Timeout(IOError):
	pass


def free(host, port, timeout=float('Inf')):
	"""
	Wait for the specified port to become free (dropping or rejecting
	requests). Return when the port is free or raise a Timeout if timeout has
	elapsed.

	Timeout may be specified in seconds or as a timedelta.
	If timeout is None or ∞, the routine will run indefinitely.
	"""
	if not host:
		raise ValueError("Host values of '' or None are not allowed.")

	if isinstance(timeout, datetime.timedelta):
		timeout = timeout.total_seconds()

	if timeout is None:
		# treat None as infinite timeout
		timeout = float('Inf')

	watch = timing.Stopwatch()

	while watch.split().total_seconds() < timeout:
		try:
			# Expect a free port, so use a small timeout
			_check_port(host, port, timeout=0.1)
			return
		except IOError:
			# Politely wait.
			time.sleep(0.1)

	raise Timeout("Port {port} not free on {host}.".format(**locals()))
wait_for_free_port = free


def occupied(host, port, timeout=float('Inf')):
	"""
	Wait for the specified port to become occupied (accepting requests).
	Return when the port is occupied or raise a Timeout if timeout has
	elapsed.

	Timeout may be specified in seconds or as a timedelta.
	If timeout is None or ∞, the routine will run indefinitely.
	"""
	if not host:
		raise ValueError("Host values of '' or None are not allowed.")

	if isinstance(timeout, datetime.timedelta):
		timeout = timeout.total_seconds()

	if timeout is None:
		# treat None as infinite timeout
		timeout = float('Inf')

	watch = timing.Stopwatch()

	while watch.split().total_seconds() < timeout:
		try:
			_check_port(host, port, timeout=.5)
			# Politely wait
			time.sleep(0.1)
		except IOError:
			# port is occupied
			return

	raise Timeout("Port {port} not bound on {host}.".format(**locals()))
wait_for_occupied_port = occupied


class HostPort(str):
	@property
	def host(self):
		host, sep, port = self.partition(':')
		return host

	@property
	def port(self):
		host, sep, port = self.partition(':')
		return int(port)


def _main():
	parser = argparse.ArgumentParser()
	global_lookup = lambda key: globals()[key]
	parser.add_argument('target', metavar='host:port', type=HostPort)
	parser.add_argument('func', metavar='state', type=global_lookup)
	parser.add_argument('-t', '--timeout', default=None, type=float)
	args = parser.parse_args()
	try:
		args.func(args.target.host, args.target.port, timeout=args.timeout)
	except Timeout as timeout:
		print(timeout, file=sys.stderr)
		raise SystemExit(1)


if __name__ == '__main__':
	_main()
