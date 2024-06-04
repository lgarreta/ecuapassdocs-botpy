#!/usr/bin/env python3

VERSION="0.86"
"""
LOG: 
 - 0.86: Mayo16: Improved Codebin conection (back) and error handling.
"""

import os, sys, time
import multiprocessing as mp
from multiprocessing import freeze_support

import signal
from threading import Thread as threading_Thread

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
from ecuapass_bot_declaracion import mainBotDeclaracion

from ecuapassdocs.info.ecuapass_feedback import EcuFeedback
from ecuapassdocs.info.ecuapass_utils import Utils

# Driver for web interaction
driver = None
def main ():
	EcuServer.start ()

def printx (*args, flush=True, end="\n"):
	print ("SERVER:", *args, flush=flush, end=end)
#-----------------------------------------------------------
# Ecuapass server: listen GUI messages and run processes
#-----------------------------------------------------------
class FlaskServer (Flask):
	def __init__(self, webdriver):
		super().__init__(__name__)
		self.webdriver = webdriver
	
print ("+++ Initializing vars: webdriver, app")
webdriver = CodebinBot.getWaitWebdriver ()
app = FlaskServer (webdriver)

class EcuServer:
	def start ():
		print ("Starting server processes...")
		serverProcess = threading_Thread (target=EcuServer.run_server_forever)
		serverProcess.start ()

		print ("Checking forced exit...")
		while not os.path.exists ("exit.txt"):
			print ("...")
			time.sleep (5)

		print ("Forced exit...")
		printx ("...Finalizando CODEBIN...")
		app.webdriver.quit ()
		printx ("...Finalizando Server...")
		serverProcess.join ()

		print ("Server terminated...")


	def run_server_forever ():
		print ("+++ run_server_forever EcuServer webdriver:", app.webdriver)

		# Start the exit thread
		#exit_thread = threading_Thread (target=EcuServer.checkForcedExit)
		#exit_thread.start ()

		# Start the server
		portNumber  = EcuServer.getPortNumber ()
		server      = make_server('127.0.0.1', portNumber, app)
		printx (f">>>>>>>>>>>>>>>> Server version: {VERSION} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
		printx (f">>>>>>>>>>>>>>>> Server is running on port::{portNumber}::<<<<<<<<<<<<<<<<<<")

		server.serve_forever()

	#----------------------------------------------------------------
	#--  Checks for a file exists to force an exit
	#----------------------------------------------------------------
	def checkForcedExit ():
		print ("+++ Startin exit thread:", os.getcwd())
		while True:
			print ("...", end="")
			if os.path.exists ("exit.txt"):
				print ("+++ Salida forzada")
				sys.exit (1)
			else:
				time.sleep(5)  # Adjust sleep time as needed	

	#----------------------------------------------------------------
	# Listen for remote calls from Java GUI
	#----------------------------------------------------------------
	@app.route('/start_processing', methods=['GET', 'POST'])
	def start_processing ():
			printx ("-------------------- Iniciando Procesamiento -------------------------")
			print ("+++ start_processing webdriver:", app.webdriver)
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
				result = EcuServer.analizeOneDocument (docFilepath=data1, runningDir=data2)

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
				result = f">>> Servicio '{service}' no disponible."

			return {'result': result}

	#----------------------------------------------------------------
	# Stop server
	#----------------------------------------------------------------
	def stop_server (runningDir):
		printx ("...Finalizando sesion CODEBIN...")
		#webdriver = CodebinBot.getWebdriver ()
		webdriver.quit ()
		#printx ("...Finalizando servidor Ecuapass...")
		#exitFilepath = os.path.join (runningDir, "exit.txt")
		#printx ("...Directorio salida: ", exitFilepath)
		#open (exitFilepath,"w").write ("")
		sys.exit (0)

	#----------------------------------------------------------------
	#-- Concurrently process one document given its path
	#----------------------------------------------------------------
	def analizeOneDocument (docFilepath, runningDir):
		workingDir = os.path.dirname (docFilepath)

		# Check if PDF is a valid ECUAPASS document
		if not EcuServer.isValidDocument (docFilepath):
			return f"Tipo de documento '{docFilepath}' no válido"

		# Create and start threads for processing files
		os.chdir (workingDir)
		ecudoc = EcuDoc ()

		message = ecudoc.extractDocumentFields (docFilepath, runningDir, app.webdriver)
		return (message)

#		TARGET = ecudoc.extractDocumentFields
#		ARGS   = (docFilepath, runningDir)
#		threading_Thread (target=TARGET, args=ARGS).start ()

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
		elif docType == "DECLARACION":
			mainBotDeclaracion (jsonFilepath, runningDir)
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
	#-- Check if document filename is an image (.png) or a PDF file (.pdf)
	#----------------------------------------------------------------
	def isValidDocument (filename):
		extension = filename.split (".")[1]
		if extension.lower() in ["PDF", "pdf"]:
			return True
		return False

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
	freeze_support ()
	main ()
