#!/usr/bin/env python3

VERSION="0.84"

import os, sys, time
import signal

from threading import Thread as threading_Thread

# For open URLs
from selenium import webdriver

# doc, bot
from ecuapass_doc import EcuDoc, mainDoc
from ecuapass_bot_cartaporte import mainBotCartaporte
from ecuapass_bot_manifiesto import mainBotManifiesto

from ecuapass_bot_cartaporte import mainBotCartaporte
from ecuapass_bot_manifiesto import mainBotManifiesto

from ecuapass_bot_declaracion import mainBotDeclaracion

# Codebin Bot
from bot_codebin import startCodebinBot
from bot_ecuapassdocs import startEcuapassdocsBot
from ecuapass_bot import EcuBot

from ecuapassdocs.info.ecuapass_feedback import EcuFeedback


#sys.stdout.reconfigure(encoding='utf-8')

# Driver for web interaction
driver = None
def main ():
	args = sys.argv
	if len (args) > 1:
		if "--version" in args:
			print ("Version: ", VERSION)
		elif "doc_processing" in args[1]:
			result = EcuServer.analizeDocuments (workingDir=args[2],
										runningDir=args [3])
		else:
			printx (f"Comando '{args[1]}' no encontrado.")

#-----------------------------------------------------------
#-----------------------------------------------------------
def printx (*args, flush=True, end="\n"):
	print ("SERVER:", *args, flush=flush, end=end)
#-----------------------------------------------------------
# Ecuapass server: listen GUI messages and run processes
#-----------------------------------------------------------
class EcuServer:
	shouldStop = False
	server = None
	runningDir = os.getcwd()

	#----------------------------------------------------------------
	# Listen for remote calls from Java GUI
	#----------------------------------------------------------------
	def start_processing (service, data1, data2):
		printx ("Iniciando procesamiento...")

		if EcuServer.shouldStop:
			return {'result': 'Servidor cerrándose...'}

		printx ("Servicio  : ", service, flush=True)
		printx ("Dato 1    : ", data1, flush=True)
		printx ("Dato 2    : ", data2, flush=True)

		# Call your existing script's function to process the file
		result = None
		if (service == "doc_processing"):
			result = EcuServer.analizeDocuments (workingDir=data1, runningDir=data2)
		elif (service == "bot_processing"):
			result = EcuServer.botProcessing (jsonFilepath=data1, runningDir=data2)

		elif (service == "codebin_transmit"):
			result = EcuServer.codebin_transmit (workingDir=data1, codebinFieldsFile=data2)

		elif (service == "ecuapassdocs_transmit"):
			result = EcuServer.ecuapassdocs_transmit (workingDir=data1, ecuapassdocsFieldsFile=data2)

		elif (service == "open_ecuapassdocs_URL"):
			EcuServer.openEcuapassdocsURL (url=data1)
		elif (service == "stop"):
			EcuServer.stop_server ()
		elif (service == "send_feedback"):
			EcuFeedback.sendFeedback (zipFilepath=data1, docFilepath=data2)
			result = "true"
		elif (service == "is_running"):
			result = "true"
		else:
			result = f">>> Servicio '{service}' no disponible."

		printx (result)
		return {'result': result}

	def stop_server ():
		printx ("Cerrando servidor Ecuapass ...")
		EcuServer.should_stop = True
		sys.exit (0)

	#----------------------------------------------------------------
	#-- Concurrently process all documents in workingDir
	#----------------------------------------------------------------
	def analizeDocuments (workingDir, runningDir):
		if workingDir is None: 
			return jsonify({'error': f"Directorio de trabajo: '{workingDir}' inválido."}), 400

		# Create and start threads for processing files
		inputFiles = [x for x in os.listdir (workingDir, ) if EcuServer.isValidDocument (x)]
		docFiles = [os.path.join (workingDir, x)  for x in inputFiles]
		threads = []
		os.chdir (workingDir)
		for docFilepath in docFiles:
			thread = threading_Thread (target=mainDoc, args=(docFilepath, runningDir,))
			threads.append (thread)
			thread.start()

		message = "Análisis exitoso de todos los documentos."
		return message
		
	#----------------------------------------------------------------
	# Open Ecuapassdocs URL in Chrome browser
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
		driver = webdriver.Chrome()
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
			Utils.printx ("ERROR: Tipo de documento desconocido: '{filename}'")
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
		if extension.lower() in ["png", "pdf"]:
			return True
		return False

	#----------------------------------------------------------------
	#-- Get document type from filename
	#----------------------------------------------------------------
	def getDoctypeFromFilename (filename):
		docType = os.path.basename (filename).split("-")[0].upper()
		if docType == "CARTAPORTE":
			return ("CARTAPORTE")
		elif docType == "MANIFIESTO":
			return ("MANIFIESTO")
		elif docType == "DECLARACION":
			return ("DECLARACION")
		else:
			Utils.printx ("ERROR: Tipo de documento desconocido: '{docType}'")
			sys.exit (1)

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()
