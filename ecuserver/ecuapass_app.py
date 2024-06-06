#!/usr/bin/env python

"""
Starts in paraller three processes: ecuserver, ecubin, ecugui.
"""
import os, sys, time, platform
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from multiprocessing import freeze_support
import subprocess

from ecuapass_server import EcuServer
from bot_codebin import CodebinBot
from ecuapass_server import result_queue, stdin_list

#------------------------------------------------------
#------------------------------------------------------
def main ():
	try:
		print ("...Using futures")
		initStartingFiles () # url_port.txt, exit.txt

		with ThreadPoolExecutor (max_workers=3)	as executor:
			webdriverFuture = executor.submit (webdriverProcess, result_queue)
			guiFuture       = executor.submit (guiProcess, stdin_list)
			time.sleep (3)
			serverFuture    = executor.submit (serverProcess)
	except Exception as ex:
		print (f"Error procesando 'future': {ex}")

#		try:
#			#serverResult = serverFuture.result ()
#			#print ("...Server result:", serverResult)
#			#guiResult   = guiFuture.result ()
#			#print ("...Gui result:", guiResult)
#			#webdriverResult   = webdriverFuture.result ()
#			#print ("...Webdriver result:", webdriverResult)
#		except Exception as ex:
#			print (f"Error procesando 'future': {ex}")

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
def serverProcess ():
	print ("+++ Starting server process...")
	EcuServer.run_server_forever ()
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
		javaCommand = ["java", "-jar", "bin/EcuapassDocsGUI.jar"]
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

