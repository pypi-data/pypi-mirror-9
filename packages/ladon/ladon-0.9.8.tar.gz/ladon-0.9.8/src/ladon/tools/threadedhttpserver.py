from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def startThreadedHTTPServer(application, host='localhost', port=8080):
	server = ThreadedHTTPServer((host, port), application)
	print 'Starting server, use <Ctrl-C> to stop'
	server.serve_forever()

