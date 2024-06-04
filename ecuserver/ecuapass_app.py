#!/usr/bin/env python

"""
Starts in paraller three processes: ecuserver, ecubin, ecugui.
"""
import os, sys, time, platform
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count, freeze_support
import threading 
import subprocess

from ecuapass_server import EcuServer


# Thread termination flag
terminate_threads = False

def main ():
	run_executor ()
#	global terminate_threads
#	# Create a new port as a consecutive of the latest port
#	initStartingFiles ()
#
#	# Create a new process
#	mainProcess = multiprocessing.Process (target=run_executor)
#	mainProcess.start()
#
#	#while not os.path.exists ("exit.txt"):
#	#	time.sleep (5)
#
#	print ("+++ Terminate threads:", terminate_threads)
#	#mainProcess.terminate ()
#	mainProcess.join ()

def run_executor ():
	executor = ThreadPoolExecutor (max_workers=2)	
	#processes = [serverProcess]
	#processes = [guiProcess]
	processes = [serverProcess, guiProcess]

	print ("......Start futures...")
	futures = [executor.submit (p) for p in processes]

	#print ("....Wait for all threads to finish...")
	for future in futures:
		future.result()


def main_processes ():
	# Create a new port as a consecutive of the latest port
	urlPort = getPortNumber ()

	num_cores = cpu_count()
	pool	  = Pool (processes=num_cores)

	print ("+++ Calling to server process")
	pool.apply_async (serverProcess, [urlPort])

	print ("+++ Calling to GUI process")
	pool.apply_async (guiProcess, [urlPort])

	print ("+++ Calling to exit process")
	stop_event = threading.Event() # Event to signal the thread to stop
	exitThread = threading.Thread (target=forcedExitProcess, args=(pool, stop_event))
	exitThread.start ()

	# Wait for tasks to finish
	print ("+++ Closing processes...")
	pool.close()

	print ("+++ Joining processes...")
	pool.join()	

	# Wait for the thread to complete
	exitThread.join()

	print ("+++ Exit")
	sys.exit (0)

#------------------------------------------------------
# Function to check for the existence of a file
#------------------------------------------------------
def forcedExitProcess (pool, stop_event):
	print ("+++ Starting exit process...")
	exitFilename = "exit.txt"
	while not stop_event.is_set():
		print ("...")
		if os.path.exists (exitFilename):
			os.remove (exitFilename)
			print(f"...Salida forzada")
			stop_event.set ()  # Signal the event to stop the thread
			pool.terminate ()
			sys.exit (0)
		else:
			time.sleep (10)  # Sleep for 1 second
#------------------------------------------------------
#------------------------------------------------------
def ecuapassCodebin ():
	CodebinBot.webdriver = CodebinBot.getWebdriver ()

#------------------------------------------------------
#------------------------------------------------------
def serverProcess ():
	print ("+++ Starting ecuapass server process...")
	EcuServer.start ()

#------------------------------------------------------
# Run the external application using subprocess.Popen
#------------------------------------------------------
def guiProcess ():
	print ("+++ Starting ecuapass GUI process...", os.getcwd())

	if platform.system () == "Windows":
		#javaCommand = ["EcuapassDocsGUI.exe"]
		javaCommand = ["EcuapassDocsGUI.bat"]
	elif platform.system () == "Linux":
		javaCommand = ["java", "-jar", "bin/EcuapassDocsGUI.jar"]
	else:
		print ("ERROR: OS no detectado")
		sys.exit (0)

#	# Run the JAR file
	process = subprocess.Popen (javaCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	# Captures the output of a subprocess and prints it in real time.
	capture_output (process)


def capture_output(process):
	"""
	Captures the output of a subprocess and prints it in real time.
	"""
	with process.stdout as pipe:
		for line in iter(pipe.readline, b''):
			# Print the line without the trailing newline character
			print (" JAVA CLIENT:", line.decode('utf-8'), end='')

#------------------------------------------------------
# Get free port by adding 1 to the last open portFilenamet
#------------------------------------------------------
def initStartingFiles ():
	print ("Buscando archivo de salida: 'exit.txt'...")
	if os.path.exists ("exit.txt"):
		os.remove ("exit.txt")

	print ("Buscando archivo de puerto: 'old_url_port.txt'...")
	portFilename	= "url_port.txt"
	portFilenameOld = "old_url_port.txt"
	
	if os.path.exists (portFilename):
		print ("\t...Renombrado archivo de puerto")
		os.rename (portFilename, portFilenameOld)

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	freeze_support ()
	main ()

