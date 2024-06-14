#!/usr/bin/env python

"""
Starts in paraller three processes: ecuapassserver, ecubin, ecugui.
"""
import os, sys, time, platform
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from multiprocessing import freeze_support
import subprocess

from ecuapassserver.ecuapass_server import EcuServer
from ecuapassserver.bot_codebin import CodebinBot
from ecuapassserver.ecuapass_server import result_queue, stdin_list

#------------------------------------------------------
#------------------------------------------------------
def main ():
	print ("-----------------------------------------------------------------")
	print ("----------------- ecuapass_app version: 0.901 -------------------")
	print ("-----------------------------------------------------------------")
	args = sys.argv

	try:
		# Check for initial files
		portNumber, settings = initStartingFiles (args) 

		# Run in three modes: Config, Debug, and Default
		with ThreadPoolExecutor (max_workers=3)	as executor:
			if settings == None: # Config: Only runs GUI to set 'settings.txt' file
				guiFuture  = executor.submit (guiProcess, stdin_list)
			elif portNumber:     # Debug: GUI is being manually run from Netbeans
				webdriverFuture = executor.submit (webdriverProcess, result_queue)
				time.sleep (3)
				serverFuture    = executor.submit (serverProcess, portNumber)
			else:                # Default: run the three threads
				guiFuture  = executor.submit (guiProcess, stdin_list)
				webdriverFuture = executor.submit (webdriverProcess, result_queue)
				time.sleep (3)
				serverFuture    = executor.submit (serverProcess, portNumber)
	except Exception as ex:
		print (f"Error procesando 'future': {ex}")

#------------------------------------------------------
# Get free port by adding 1 to the last open portFilenamet
#------------------------------------------------------
def initStartingFiles (args):
	portNumber = None
	settings   = None

	if len (args) > 1:
		portNumber = args [1]
		print (f"Running on a user port number: '{portNumber} ")

	print ("Buscando archivo de salida: 'exit.txt'...")
	if os.path.exists ("exit.txt"):
		os.remove ("exit.txt")

	print ("Buscando archivo de puerto: 'old_url_port.txt'...")
	portFilename	= "url_port.txt"
	oldPortFilename = "old_url_port.txt"
	
	if os.path.exists (portFilename):
		print ("\t...Renombrado archivo de puerto")
		os.rename (portFilename, oldPortFilename)

	# Check if "settings.txt" exists
	if os.path.exists ("settings.txt"):
		settings = True

	return (portNumber, settings)


#------------------------------------------------------
# Load webdriver
#------------------------------------------------------
def webdriverProcess (result_queue):
	print ("+++ Starting webdriver process...")
	webdriver = CodebinBot.getWaitWebdriver ()
	result_queue.append (webdriver)
	return ("Wedriver process has finished")

#------------------------------------------------------
# Run flask server
#------------------------------------------------------
def serverProcess (portNumber=None):
	print ("+++ Starting server process...", portNumber)

	# Called from command line
	EcuServer.run_server_forever (portNumber)

	return ("EcuServer process has finished")
#------------------------------------------------------
# Run the external application using subprocess.Popen
#------------------------------------------------------
def guiProcess (stdin_list):
	print ("+++ Starting GUI process...")

	if platform.system () == "Windows":
		javaCommand = ["EcuapassDocsGUI.exe"]
		#javaCommand = ["EcuapassDocsGUI.bat"]
	elif platform.system () == "Linux":
		javaCommand = ["java", "-jar", "EcuapassDocsGUI.jar"]
	else:
		print ("ERROR: OS no detectado")
		sys.exit (0)

	# Run Java GUI and captures its output to print it in real time.
	process = subprocess.Popen (javaCommand, stdin=subprocess.PIPE, 
	                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdin_list.append (process)
	#outputThread = Thread (target=capture_output, args=(process,))
	#outputThread.start ()
	capture_output (process)
	

	return "Gui process has finished"

#------------------------------------------------------
#-- Captures the output of a subprocess and prints it in real time.
#------------------------------------------------------
def capture_output (process):
	with process.stdout as pipe:
		for line in iter (pipe.readline, b''):
			try:
				# Decode with UTF-8 and strip whitespaces
				decoded_line = line.decode('utf-8')
				print("JAVA CLIENT:", decoded_line, end='')
			except UnicodeDecodeError:
				print ("JAVA CLIENT:", line, end='')
				print("Error decoding output. Using a different encoding might be necessary.")

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	freeze_support ()
	main ()

