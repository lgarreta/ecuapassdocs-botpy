#!/usr/bin/env python

"""
Starts in paraller three processes: ecuserver, ecubin, ecugui.
"""
import os, sys, time
import multiprocessing as mp
from multiprocessing import Pool, cpu_count
import threading 
import subprocess

from bot_codebin import CodebinBot
from ecuapass_server import EcuServer

#------------------------------------------------------
#------------------------------------------------------
#def exitProcess (serverProcess, guiProcess):
def exitProcess (pool):
	print ("+++ Starting exit process...")
	exitFilename = "exit.txt"
	while True:
		print ("+++ Verificando salida forzada...")
		if os.path.exists (exitFilename):
			os.remove (exitFilename)
			print ("\t...Salida forzada")
			pool.terminate ()
			#serverProcess.terminate()
			#guiProcess.terminate()
			sys.exit (0)
		else:
			time.sleep(10)	# Adjust sleep time as needed	

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
	print ("+++ Starting ecuapass GUI process...")

	#jarCommand = ["java", "-jar", "EcuapassDocsAnalisisGUI.jar"]
	#javaCommand = ["EcuapassDocsGUI.exe"]
	javaCommand = ["java", "-jar", "bin/EcuapassDocsGUI.jar"]
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
		# read old port
		with open (portFilename, "r") as portFile: 
			portString = portFile.readline ()
			portNumber = int (portString) + 1

		# write new port
		with open (portFilename, "w") as portFile: 
			portFile.write ("%d" % portNumber)

		print ("\t...Usando el puerto:", portNumber)

		return (portNumber)

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
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
	exitThread = threading.Thread (target=exitProcess, args=(pool,))
	exitThread.start ()

	#pool.apply_async (exitProcess, ["serverProcess", "guiProcess"])

	# Wait for tasks to finish
	print ("+++ Closing processes...")
	pool.close()

	print ("+++ Joining processes...")
	pool.join()	

	print ("+++ Exit")
	sys.exit (0)

	#tasks = [(serverProcess,[urlPort]), (guiProcess, [urlPort])]
	#print ("+++ tasks:", tasks)

	# Send tasks to the pool using starmap
	#results = pool.starmap (tasks)

#	# Create the processes
#	ecuserverProcess = mp.Process (target=serverProcess, args=(urlPort,))
#	guiProcess		 = mp.Process (target=guiProcess, args=(urlPort,))
#	#exitProcess		 = mp.Process (target=checkForcedExit,)
#	#codebinProcess	 = mp.Process (target=ecuapassCodebin)
#
#	#processList = [ecuserverProcess, codebinProcess, guiProcess]
#	processList = [ecuserverProcess, guiProcess]
#
#	# Start the processes	
#	for process in processList:
#		process.start ()
#
#	# Wait for the processes to finish 
#	for process in processList:
#		process.join ()
#	
	sys.exit (0)

