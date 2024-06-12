import os
from flask import Flask, request
import threading
import time

app = Flask(__name__)

# Global variable to store the last request time
last_request_time = time.time()

# Function to handle requests
@app.route('/')
def index():
	global last_request_time
	last_request_time = time.time()  # Update last request time
	return "Hello, World!"

@app.route('/stop')
def stop ():
	shutdown_server ()

# Background thread to check the last request time
def check_server_activity():
	global last_request_time
	timeout_duration = 60 * 5  # 5 minutes in seconds
	while True:
		if time.time() - last_request_time > timeout_duration:
			print("No activity for {} minutes. Stopping server...".format(timeout_duration / 60))
			shutdown_server()
			break
		time.sleep(60)	# Check every minute

# Function to shutdown the Flask server
def shutdown_server():
	print ("...Shutting down the server") 
	#app.stop_serving()
	#request.environ['wsgi.server'].shutdown()
	os._exit (0)
	#func = request.environ.get('werkzeug.server.shutdown')
	#if func:
	#	func()
	return ("Server has been stopped")

# Start the background thread to check server activity
check_thread = threading.Thread(target=check_server_activity)
check_thread.daemon = True
check_thread.start()

if __name__ == '__main__':
	app.run()

