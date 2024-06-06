#!/usr/bin/env python3

VERSION="0.900"
"""
LOG: 
Jun/06 : 0.900 : Redesigned as three independent process: GUI, Server, webdrive
May/16 : 0.860 : Improved Codebin conection (back) and error handling.
"""

import os, sys, time
import multiprocessing as mp

# Threads
from threading import Thread 
import queue

# For server
from flask import Flask 
from flask import request as flask_request 
from werkzeug.serving import make_server

# Codebin, Ecuapassdocs Bot
from bot_codebin import CodebinBot
from bot_codebin import startCodebinBot
from bot_ecuapassdocs import startEcuapassdocsBot

# doc, document bots
from ecuapass_doc import EcuDoc
from ecuapass_bot_cartaporte import mainBotCartaporte
from ecuapass_bot_manifiesto import mainBotManifiesto

from ecuapassdocs.info.ecuapass_feedback import EcuFeedback
from ecuapassdocs.info.ecuapass_utils import Utils

# Driver for web interaction
driver = None
def main ():
	EcuServer.start ()

#-----------------------------------------------------------
# Ecuapass server: listen GUI messages and run processes
#-----------------------------------------------------------
class FlaskServer (Flask):
	def __init__(self, result_queue):
		super().__init__(__name__)
		self.queue = result_queue

	def getWebdriver (self):
		#self.webdriver = self.queue.get () 
		self.webdriver = self.queue [0]
		return self.webdriver

	def stopWebdriver (self):
		self.webdriver.quit ()

#-----------------------------------------------------------
# Global vars
#-----------------------------------------------------------
result_queue = list ()   # To put/get webdriver
stdin_list   = list ()   # To put/get java GUI stdin and used by python Server
app = FlaskServer (result_queue)

#-----------------------------------------------------------
#-----------------------------------------------------------
def printx (*args, flush=True, end="\n"):
	print ("SERVER2:", *args, flush=flush, end=end)
#	print ("STDIN:", stdin_list[0])
#	if len (stdin_list) > 0:
#		guiProcess = stdin_list [0]
#		text = " ".join (args)
#		guiProcess.stdin.write ("HOLA".encode())
#		guiProcess.stdin.close ()

#-----------------------------------------------------------
#-----------------------------------------------------------
class EcuServer:
	#-- Start server and webdriver
	def start ():
		run_server_forever ()
#		flaskProcess = Thread (target=EcuServer.run_server_forever)
#		flaskProcess.start ()

#		webdriverProcess = Thread (target=EcuServer.getWebdriver, args=(result_queue,))
#		webdriverProcess.start ()

#		flaskProcess.join ()
#		webdriverProcess.join ()

	#-- Start the server
	def run_server_forever ():
		portNumber  = EcuServer.getPortNumber ()
		server      = make_server('127.0.0.1', portNumber, app)
		printx (f">>>>>>>>>>>>>>>> Server version: {VERSION} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
		printx (f">>>>>>>>>>>>>>>> Server is running on port::{portNumber}::<<<<<<<<<<<<<<<<<<")

		server.serve_forever()

	#----------------------------------------------------------------
	# Listen for remote calls from Java GUI
	#----------------------------------------------------------------
	@app.route('/start_processing', methods=['GET', 'POST'])
	def start_processing ():
		try:
			printx ("-------------------- Iniciando Procesamiento -------------------------")
			webdriver = app.getWebdriver ()
			# Get the file name from the request
			service = flask_request.json ['service']
			data1   = flask_request.json ['data1']
			data2   = flask_request.json ['data2']

			printx ("Servicio  : ", service, flush=True)
			printx ("Dato 1    : ", data1, flush=True)
			printx ("Dato 2    : ", data2, flush=True)

			# Call your existing script's function to process the file
			result = None
			if (service == "doc_processing"):
				result = EcuDoc.analyzeDocument (docFilepath=data1, runningDir=data2, webdriver=webdriver)

			elif (service == "bot_processing"):
				result = EcuServer.botProcessing (jsonFilepath=data1, runningDir=data2)

			elif (service == "codebin_transmit"):
				result = EcuServer.codebin_transmit (workingDir=data1, codebinFieldsFile=data2)

			elif (service == "ecuapassdocs_transmit"):
				result = EcuServer.ecuapassdocs_transmit (workingDir=data1, ecuapassdocsFieldsFile=data2)

			elif (service == "open_ecuapassdocs_URL"):
				EcuServer.openEcuapassdocsURL (url=data1)

			elif (service == "stop"):
				printx ("...Attending 'stop_server'...") 
				EcuServer.stop_server (runningDir=data1)

			elif (service == "send_feedback"):
				EcuFeedback.sendFeedback (zipFilepath=data1, docFilepath=data2)
				result = "true"

			elif (service == "is_running"):
				result = "true"

			else:
				print (f"Servicio '{service}' no existe")
				result = f">>> Servicio '{service}' no disponible."

			return result
		except Exception as ex:
			print (f"Error en start_processing: '{ex}'")

	#----------------------------------------------------------------
	# Stop server
	#----------------------------------------------------------------
	def stop_server (runningDir):
		print ("Finalizando servidor...")
		print ("...Finalizando CODEBIN")
		app.stopWebdriver ()
		sys.exit (0)

	#----------------------------------------------------------------
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	# Open Ecuapassdocs URL in Chrome browser
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def openEcuapassdocsURL (url):
		import pyautogui as py

		windows = py.getAllWindows ()
		printx (">> Todas las ventanas:", [x.title for x in windows])
		for win in windows:
			if "EcuapassDocs" in win.title and "Google" in win.title:
				win.minimize()
				win.restore (); py.sleep (1)
				return

		global driver
		if driver:
			driver.quit ()
		print (">> Inicializando webdriver...")
		driver = selenium.webdriver.Chrome()
		driver.get (url)

		#printx (f">> Abriendo sitio web de EcuapassDocs: '{url}'")
		#driver.execute_script("window.open('" + url + "','_blank');")

#		# Check if the URL is already open in another window
#		url_open = False
#		printx (f">> Buscando una ventana abierta de EcuapassDocs : '{url}'")
#		for handle in driver.window_handles:
#			driver.switch_to.window (handle)
#			print (f">>>> Ventana : '{driver.current_url}'")
#			current_url = driver.current_url
#			if url == current_url:
#				url_open = True
#				break
#
#
#		# Optionally, switch to the last opened window
#		driver.switch_to.window(driver.window_handles[-1])
		
		
	#----------------------------------------------------------------
	#-- Execute bot according to the document type
	#-- Doctype is in the first prefix of the jsonFilepath
	#----------------------------------------------------------------
	def botProcessing (jsonFilepath, runningDir):
		docType = EcuServer.getDoctypeFromFilename (jsonFilepath)

		if docType == "CARTAPORTE":
			mainBotCartaporte (jsonFilepath, runningDir)
		elif docType == "MANIFIESTO":
			mainBotManifiesto (jsonFilepath, runningDir)
		else:
			printx ("ERROR: Tipo de documento desconocido: '{filename}'")
			sys.exit (0)

	#----------------------------------------------------------------
	#-- Transmit document fields to CODEBIN web app using Selenium
	#----------------------------------------------------------------
	def codebin_transmit (workingDir, codebinFieldsFile):
		filepath = os.path.join (workingDir, codebinFieldsFile)
		docType = EcuServer.getDoctypeFromFilename (codebinFieldsFile)
		startCodebinBot (docType, filepath)

	#----------------------------------------------------------------
	#-- Transmit document fields to ECUAPASSDOCS web app using Selenium
	#----------------------------------------------------------------
	def ecuapassdocs_transmit (workingDir, ecuapassdocsFieldsFile):
		filepath = os.path.join (workingDir, ecuapassdocsFieldsFile)
		docType = EcuServer.getDoctypeFromFilename (ecuapassdocsFieldsFile)
		startEcuapassdocsBot (filepath)

	#----------------------------------------------------------------
	#-- Get document type from filename
	#----------------------------------------------------------------
	def getDoctypeFromFilename (filename):
		docType = os.path.basename (filename).split("-")[0].upper()
		filename = filename.upper ()
		if "CPI" in filename or "CARTAPORTE" in filename:
			return ("CARTAPORTE")
		elif "MCI" in filename or "MANIFIESTO" in filename:
			return ("MANIFIESTO")
		elif "DCL" in filename or "DECLARACION" in filename:
			return ("DECLARACION")
		else:
			printx (f"ERROR: Tipo de documento desconocido: '{docType}'")
			sys.exit (1)

	#------------------------------------------------------
	# Get free port by adding 1 to the last open port
	#------------------------------------------------------
	def getPortNumber ():
		portFilename    = "url_port.txt"
		oldPortFilename = "old_url_port.txt"
		portNumber = 5000
		
		# read old port
		if os.path.exists (oldPortFilename):
			with open (oldPortFilename, "r", encoding='utf-8') as portFile: 
				portString = portFile.readline ()
				portNumber = 1 + int (portString)
			os.remove (oldPortFilename)

		# write new port
		print ("+++ Escribiendo nuevo puerto: ", portNumber)
		with open (portFilename, "w", encoding='utf-8') as portFile: 
			portFile.write ("%d" % portNumber)

		return portNumber

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	mp.freeze_support ()
	main ()
