#!/usr/bin/env python

"""
Starts in paraller three processes: ecuserver, ecubin, ecugui.
"""
import os, sys, time
from multiprocessing import Pool, cpu_count, freeze_support
import threading 
import subprocess

from bot_codebin import CodebinBot
from ecuapass_server import EcuServer

def main ():
	# Create a new port as a consecutive of the latest port
	urlPort = getPortNumber ()

	print ("+++ Getting the number of available CPU cores")
	num_cores = cpu_count()

	print ("+++ Creating a pool with the system's core count:", num_cores)
	pool = Pool (processes=num_cores)

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
#------------------------------------------------------
#def forcedExitProcess (serverProcess, guiProcess):
#	print ("+++ Starting exit process...")
#	exitFilename = "exit.txt"
#	while True:
#		print ("+++ Verificando salida forzada...")
#		if os.path.exists (exitFilename):
#			os.remove (exitFilename)
#			print ("\t...Salida forzada")
#			pool.terminate ()
#			#serverProcess.terminate()
#			#guiProcess.terminate()
#			sys.exit (0)
#		else:
#			time.sleep(10)	# Adjust sleep time as needed	

# Function to check for the existence of a file
def forcedExitProcess (pool, stop_event):
	print ("+++ Starting exit process...")
	exitFilename = "exit.txt"
	while not stop_event.is_set():
		print ("+++ Verificando salida forzada...")
		if os.path.exists (exitFilename):
			os.remove (exitFilename)
			print(f"...Salida forzada")
			stop_event.set ()  # Signal the event to stop the thread
			pool.terminate ()
			sys.exit (0)
		else:
			time.sleep (15)  # Sleep for 1 second
#------------------------------------------------------
#------------------------------------------------------
def ecuapassCodebin ():
	CodebinBot.webdriver = CodebinBot.getWebdriver ()

#------------------------------------------------------
#------------------------------------------------------
def serverProcess (urlPort):
	print ("+++ Starting ecuapass server process...")

	EcuServer.run_server_forever()

#------------------------------------------------------
# Run the external application using subprocess.Popen
#------------------------------------------------------
def guiProcess (urlPort):
	print ("+++ Starting ecuapass GUI process...", os.getcwd())

	#jarCommand = ["java", "-jar", "EcuapassDocsAnalisisGUI.jar"]
	javaCommand = ["EcuapassDocsGUI.exe"]
#	javaCommand = ["java", "-jar", "bin/EcuapassDocsGUI.jar"]
#
#	# Run the JAR file
	process = subprocess.Popen (javaCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
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
def getPortNumber ():
	print ("Buscando archivo de puerto: 'url_port.txt'...")
	portFilename	= "url_port.txt"
	portFilenameOld = "old_url_port.txt"
	portNumber = 5000
	
	if not os.path.exists (portFilename):
		print ("\t...Archivo de puerto no existe")
		sys.exit (1)
	else:
		# Read old port
		with open (portFilename, "r") as portFile: 
			portNumber = int (portFile.readline ()) + 1
		# Write new port
		with open (portFilename, "w") as portFile: 
			portFile.write ("%d" % portNumber)

		print ("\t...Usando el puerto:", portNumber)

		return (portNumber)

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	freeze_support ()
	main ()

