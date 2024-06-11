#!/usr/bin/env python3

"""
Type document (json file) to ECUAPASSDOCS web 
"""
import sys, json, re, time, os
import PyPDF2

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.resourceloader import ResourceLoader 

#----------------------------------------------------------
# Main
#----------------------------------------------------------
def main ():
	args = sys.argv

	docFieldsFile = args [1]   # PDF with Ecudoc fields
	mainDocBot (docFieldsFile)

#----------------------------------------------------------------
# mainDocBot
#----------------------------------------------------------------
def startEcuapassdocsBot (ecuapassdocsFieldsFile):
	botDoc = DocBot (ecuapassdocsFieldsFile)
	botDoc.run ()

#----------------------------------------------------------------
# Bot for filling CODEBIN forms from ECUDOCS fields info
#----------------------------------------------------------------
class DocBot:
	def __init__ (self, docFieldsFile):
		self.url           = "https://ecuapassdocs-test.up.railway.app/"
		#self.url           = "http://127.0.0.1:8000/"
		self.docFieldsFile = docFieldsFile
		self.driver        = None
		self.docType       = self.getDocumentTypeFromFilename (docFieldsFile)

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def run (self):
		filename = os.path.basename (self.docFieldsFile)
		Utils.printx (f">> Transmitiendo '{self.docType}' '{filename}' a ECUAPASSDOCS")

		docFields = json.load (open (self.docFieldsFile))
		pais = self.getPais (docFields)

		self.login (pais)

		frameDocumento = self.nuevoDocumento (self.docType, pais)

		self.fillForm (frameDocumento, docFields)

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def getPais (self, docFields):
		pais = docFields ["txt0a"]
		Utils.printx (">>> Pais:", pais)
		return pais

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def login (self, pais):
		# Open and click on "Continuar" button
		driver = webdriver.Chrome ()
		#driver.get ("http://127.0.0.1:8000/")
		driver.get (self.url)
		iniciarSesionLink = driver.find_element (By.LINK_TEXT, "Iniciar sesión")
		iniciarSesionLink.click ()

		# Open new window login form, and login with "admin"/"admin"
		time.sleep (0.5)
		loginForm = driver.find_element (By.TAG_NAME, "form")
		userInput = loginForm.find_element (By.NAME, "username")
		userInput.send_keys ("admin")
		userInput = loginForm.find_element (By.NAME, "password")
		userInput.send_keys ("admin")
		submit_button = loginForm.find_element (By.ID, "submit")
		submit_button.click()

		self.driver = driver
		
	#-------------------------------------------------------------------
	# Click "Cartaporte"|"Manifiesto" then "Nuevo" returning document frame
	#-------------------------------------------------------------------
	def nuevoDocumento (self, docType, pais):
		try:
			driver = self.driver
			menuString = ""
			if docType == "CARTAPORTE" and pais == "CO":
				menuString = "Cartaporte Importación"
			elif docType == "CARTAPORTE" and pais == "EC":
				menuString = "Cartaporte Exportación"
			elif docType == "MANIFIESTO" and pais == "CO":
				menuString = "Manifiesto Importación"
			elif docType == "MANIFIESTO" and pais == "EC":
				menuString = "Manifiesto Exportación"
			else:
				print (f"Tipo desconocido de documento '{docType}'")
				sys.exit (0)

			# Select new document opening a new tab
			link = driver.find_element (By.PARTIAL_LINK_TEXT, menuString)
			link.click()

			# Get handles of all windows and switch to the new tab
			all_windows = driver.window_handles
			driver.switch_to.window (all_windows[1])

			# Get the document form and return it
			docForm = driver.find_element(By.ID, "forma_pdf")	# Find the form by ID

			return docForm

		except Exception as e:
			Utils.printException("No se pudo crear documento nuevo en ECUAPASSDOCS")
			return None

	#-----------------------------------------------------------
	#-- Fill document web form fields with ECUDOC fields
	#-- Skip or do special handling for some fields 
	#-----------------------------------------------------------
	def fillForm (self, docForm, docFields):
		CARTAPORTE  = self.docType == "CARTAPORTE"
		MANIFIESTO  = self.docType == "MANIFIESTO"
		DECLARACION = self.docType == "DECLARACION"

		for field in docFields.keys():

			value = docFields [field]
			if not value:
				continue

			# Skip "pais", "transportista", and totals
			if CARTAPORTE and field in ["txt0a", "txt01", "txt17_14", "txt17_34"]:
				continue

			# Skip data copied from reception data
			elif CARTAPORTE and field in ["txt07", "txt19"]:
				continue

			# Skip "pais", "permision" fields, and totals
			elif MANIFIESTO and field in ["txt0a", "txt01", "txt02", "txt03"]:
				continue

			# Select one "tipo de carga"
			elif MANIFIESTO and field in ["txt25_1", "txt25_2", "txt25_3", "txt25_4"]:
				elem = docForm.find_element (By.ID, field)
				value = "X" if value == 1 else ""
				elem.send_keys (value)

			# Skip default values of aduanas "cruce y destino"
			elif MANIFIESTO and field in ["txt37", "txt38"]:
				continue

#			# Tomados de la BD del vehículo y de la BD del conductor
#			elif MANIFIESTO and field in ["a9", "a10", "a11", "a12"] and \
#				field in ["a19", "a20", "a21", "a22"]:
#				continue  
#
#			# Tomados de la BD de la cartaporte 
#			elif MANIFIESTO and field in ["a29","a30","a31","a32a","a32b",
#			                              "a33","a34a","a34b","a34c","a34d","a40"]:
#				continue  

			else:
				elem = docForm.find_element (By.NAME, field)
				#elem.click ()
				elem.send_keys (value.replace ("\r\n", "\n"))

	#-----------------------------------------------------------
	#-- Get type of document from filename (e.g CPI-XXX.pdf or CARTAPORTE-XXX.pdf 
	#-----------------------------------------------------------
	def getDocumentTypeFromFilename (self, filepath):
		filename = os.path.basename (filepath).upper()
		if "CARTAPORTE" in filename or "CPI" in filename:
			return "CARTAPORTE"
		elif "MANIFIESTO" in filename or "MCI" in filename:
			return "MANIFIESTO"
		elif "DECLARACION" in filename or "DCL" in filename:
			return "DECLARACION"
		else:
			print (f"Tipo de documento desconocido en archivo: '{filename}'")
		return None

	#----------------------------------------------------------------
	# Not Used:
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


#-----------------------------------------------------------
# Call to main
#-----------------------------------------------------------
if __name__ == "__main__":
	main()
