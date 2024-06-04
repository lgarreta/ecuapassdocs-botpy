#!/usr/bin/env python3

"""
Fill CODEBIN web form from JSON fields document.
"""
import sys, json, re, time, os
import PyPDF2

from threading import Thread as threading_Thread

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.resourceloader import ResourceLoader 
from ecuapassdocs.info.ecuapass_info_cartaporte import CartaporteInfo

#----------------------------------------------------------
# Main
#----------------------------------------------------------
def main ():
	args = sys.argv
	option = args [1]
	print ("--option:", option)

	if "--getEcudocsValues" in option:
		print (">> Running getEcudocsValues...")
		pdfFilepath = args [2]
		codebinBot = CodebinBot ("BYZA")
		codebinBot.getEcudocsValuesFromCodebinWeb (pdfFilepath)
		
	elif "--getcodebinvalues" in option:
		#---- Extract data from CODEBIN --------------------------------- 
		botCodebin = CodebinBot ()
		botCodebin.getValuesFromRangeCodebinCartaportes ("colombia")

	elif "--cleancodebincartaportes" in option:
		#---- Remove invalid records (e.g. no remitente)
		inDir = args [2]
		cleanCodebinCartaportesFiles (inDir)

#-------------------------------------------------------------------
# Get document values from CODEBIN web using PDF file doc number
#-------------------------------------------------------------------
def mainGetValuesFromCodebinWeb (pdfFilepath, settings):
	try:
		webdriver = CodebinBot.getWebdriver ()
		bot       = CodebinBot (settings, webdriver, pdfFilepath)

		# Call to bot to get values from CODEBIN web
		codebinValues = None
		codebinValues = bot.getValuesFromCodebinWeb (bot.docNumber, bot.pais, bot.codigoPais)

		# Format to Azure values
		azureValues = Utils.getAzureValuesFromCodebinValues (bot.docType, codebinValues, bot.docNumber)
		# Save data
		outCbinFilename = f"{bot.docType}-{bot.empresa}-{bot.docNumber}-CBINFIELDS.json"
		outDocFilename  = f"{bot.docType}-{bot.empresa}-{bot.docNumber}-DOCFIELDS.json"
		json.dump (codebinValues, open (outCbinFilename, "w"), indent=4)
		json.dump (azureValues, open (outDocFilename, "w"), indent=4, sort_keys=True)

		return outDocFilename
	except DocumentNotFoundException as ex:
		raise ex
	except:
		raise Exception ("Intentelo nuevamente. Problemas conectando con CODEBIN.") 
		#Utils.printx (f"ALERTA: Problemas al conectarse con CODEBIN. Revise URL, usuario y contraseña") 
		Utils.printException ()

	return None

#----------------------------------------------------------------
# Bot for filling CODEBIN forms from ECUDOCS fields info
#----------------------------------------------------------------
class CodebinBot:
	def setSettings (self, pdfFilepath, settings, webdriver):
		self.settings = settings
		self.empresa  = settings ["empresa"]
		self.url      = settings ["codebin_url"]
		self.user     = settings ["codebin_user"]
		self.password = settings ["codebin_password"]

		# Init bot settings
		self.docNumber             = self.getDocumentNumberFromFilename (pdfFilepath) # Special for NTA
		self.docType               = Utils.getDocumentTypeFromFilename (pdfFilepath)
		self.pais, self.codigoPais = Utils.getPaisCodigoFromDocNumber (self.docNumber)
		self.user, self.password   = self.getUserPasswordForEmpresaPais (self.empresa, self.pais)

		self.webdriver             = webdriver

	def initWebdriver (self):
		Utils.printx ("Initializing webdriver...")
		options = Options()
		options.add_argument("--headless")
		self.IS_OPEN = False
		self.LAST_PAIS = ""
		self.webdriver = webdriver.Firefox (options=options)
		Utils.printx ("...webdriver initialized")
		return self.webdriver
	#------------------------------------------------------
	# Used 
	#------------------------------------------------------
	@staticmethod
	def getWaitWebdriver ():
		Utils.printx ("Getting webdriver...")
		while not hasattr (CodebinBot, "webdriver"):
			Utils.printx ("Loading webdriver...")
			options = Options()
			options.add_argument("--headless")
			CodebinBot.IS_OPEN = False
			CodebinBot.LAST_PAIS = ""
			CodebinBot.webdriver = webdriver.Firefox (options=options)
			Utils.printx ("...webdriver Loaded")
		return CodebinBot.webdriver
	#------------------------------------------------------
	#------------------------------------------------------
	def getDocumentFile (self):
		try:
			# Call to bot to get values from CODEBIN web
			codebinValues = None
			codebinValues = self.getValuesFromCodebinWeb (self.docNumber, self.pais, self.codigoPais)

			# Format to Azure values
			azureValues = Utils.getAzureValuesFromCodebinValues (self.docType, codebinValues, self.docNumber)
			# Save data
			outCbinFilename = f"{self.docType}-{self.empresa}-{self.docNumber}-CBINFIELDS.json"
			outDocFilename  = f"{self.docType}-{self.empresa}-{self.docNumber}-DOCFIELDS.json"
			json.dump (codebinValues, open (outCbinFilename, "w"), indent=4)
			json.dump (azureValues, open (outDocFilename, "w"), indent=4, sort_keys=True)

			return outDocFilename
		except DocumentNotFoundException as ex:
			raise ex
		except:
			raise Exception ("Intentelo nuevamente. Problemas conectando con CODEBIN.") 
			#Utils.printx (f"ALERTA: Problemas al conectarse con CODEBIN. Revise URL, usuario y contraseña") 
			Utils.printException ()

		return None

	#------------------------------------------------------
	#------------------------------------------------------
	def getUserPasswordForEmpresaPais (self, empresa, pais):
		user, password = None, None
		if empresa == "NTA" and pais.upper() == "COLOMBIA":
			user      = self.settings ["codebin_user"]
			password  = self.settings ["codebin_password"]
		elif empresa == "NTA" and pais.upper() == "ECUADOR":
			user      = self.settings ["codebin_user2"]
			password  = self.settings ["codebin_password2"]
		else: # Default: for most companies
			user      = self.settings ["codebin_user"]
			password  = self.settings ["codebin_password"]

		return user, password

	#-------------------------------------------------------------------
	# Get the number (ej. CO00902, EC03455) from the filename
	#-------------------------------------------------------------------
	def getDocumentNumberFromFilename (self, filename):
		numbers = re.findall (r"\w+\d+", filename)
		docNumber = numbers [-1]

		if self.empresa == "NTA":
			docNumber = docNumber.replace ("COCO", "CO")
			docNumber = docNumber.replace ("ECEC", "EC")

		return docNumber

	#------------------------------------------------------
	# Start Firefox Web Server for CODEBIN session
	#------------------------------------------------------
	@staticmethod
	def getWebdriver ():
		print ("+++ Getting webdriver...")
		while not hasattr (CodebinBot, "webdriver"):
			Utils.printx ("...Waiting for Codebin webdriver")
			time.sleep (2)
		return CodebinBot.webdriver

	@staticmethod
	def initCodebinWebdriver ():
		Utils.printx (">>>>>>>>>>>>>>>> Iniciando CODEBIN firefox <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

		def funThreadFirefox ():
			options = Options()
			options.add_argument("--headless")
			#options.add_argument('--disable-extensions')
			#options.add_argument('--blink-settings=imagesEnabled=false')
			CodebinBot.IS_OPEN = False
			CodebinBot.LAST_PAIS = ""
			CodebinBot.webdriver = webdriver.Firefox (options=options)
			Utils.printx (">>>>>>>>>>>>>>>> CODEBIN firefox is running <<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

		threadFirefox = threading_Thread (target=funThreadFirefox, args=())
		threadFirefox.start ()

	#-------------------------------------------------------------------
	#-- Get the CODEBIN id from document number
	#-- List documents, search the number, and get the id of selected
	#-------------------------------------------------------------------
	def getValuesFromCodebinWeb (self, docNumber, pais, codigoPais):
		print ("+++ Getting values from Codebin web...")
		try:
			self.openCodebin (pais)

			urlSettings  = self.getCodebinUrlSettingsForEmpresa ()
			textMainmenu = urlSettings ["menu"]
			textSubmenu  = urlSettings ["submenu"]
			documentUrl  = urlSettings ["link"]

			searchField, docsTable = self.getCodebinSearchElements (textMainmenu, textSubmenu) 
			searchField.send_keys (docNumber)

			# Get table, get row, and extract id
			docId = self.getCodebinDocumentId (docsTable, docNumber)

			# Get CODEBIN link for document with docId
			self.webdriver.get (documentUrl % docId)

			# Get Codebin values from document form
			docForm       = self.webdriver.find_element (By.TAG_NAME, "form")
			codebinValues = self.getCodebinValuesFromCodebinForm (docForm, codigoPais, docNumber)

			self.closeInitialCodebinWindow ()
			CodebinBot.LAST_PAIS = pais
			CodebinBot.IS_OPEN   = True

			return codebinValues
		except:
			self.quitCodebin ()
			raise


	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def getCodebinDocumentId (self, docsTable, docNumber):
		docId = None
		try:
			#table   = container.find_element (By.TAG_NAME, "table")
			docLink    = docsTable.find_element (By.PARTIAL_LINK_TEXT, docNumber)
			idText     = docLink.get_attribute ("onclick")
			textLink   = docLink.text
			docId      = re.findall (r"\d+", idText)[-1]

			Utils.printx (f"+++ Documento buscado: '{docNumber}' : Documento encontrado: '{textLink}'")
			if docNumber != textLink.strip():
				message = f"Documento número: '{docNumber}' no existe en CODEBIN"
				raise DocumentNotFoundException (message)
		except NoSuchElementException:
			raise
		except:
			raise
		return docId

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def quitCodebin (self):
		if CodebinBot.webdriver:
			CodebinBot.webdriver.quit ()

		CodebinBot.webdriver = None
		CodebinBot.IS_OPEN   = False

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def getCodebinSearchElements (self, textMainmenu, textSubmenu):
		# Select menu Carta Porte I
		cpi = self.webdriver.find_element (By.PARTIAL_LINK_TEXT, textMainmenu)
		cpi.click ()

		# Select submenu 'Lista'
		cpi_lista = self.webdriver.find_element (By.XPATH, f"//a[contains(@href, '{textSubmenu}')]")
		cpi_lista.click ()

		# Get and swithc to frame 'Lista'
		cpi_lista_object = self.webdriver.find_element (By.TAG_NAME, "object")
		wait = WebDriverWait (self.webdriver, 2)
		wait.until (EC.frame_to_be_available_and_switch_to_it (cpi_lista_object))
		time.sleep (1)

		# get and set number into input 'Buscar'
		cpi_lista_container = self.webdriver.find_elements (By.CLASS_NAME, "container")
		container           = cpi_lista_container [0]
		time.sleep (1)
		searchField    = container.find_element (By.TAG_NAME, "input")
		searchTable    = container.find_element (By.TAG_NAME, "table")

		return searchField, searchTable 

	#-------------------------------------------------------------------
	# Close initial codebin windows
	#-------------------------------------------------------------------
	def closeInitialCodebinWindow (self):
		print ("-- Cerrando ventana inicial de CODEBIN")
		# Store the handle of the original window
		original_window = self.webdriver.current_window_handle	

		for handle in self.webdriver.window_handles:
			self.webdriver.switch_to.window (handle)
			current_title = self.webdriver.title

			if "GRUPO BYZA SAS" in current_title or \
			"NUEVO TRANSPORTE DE AMERICA CIA LTDA" in current_title:
				self.webdriver.close()  # Close the window with the matching title
				break  # Exit the loop once the target window is closed		

		self.webdriver.switch_to.window (original_window)

	#-------------------------------------------------------------------
	# Initial browser opening
	# Open codebin session for new docs or go back to begina a new search
	#-------------------------------------------------------------------
	def openCodebin (self, pais):
		if CodebinBot.IS_OPEN and CodebinBot.LAST_PAIS == pais:
			print ("+++ Going CODEBIN back...")
			self.webdriver.back ()    # Search results
		else:
			print ("+++ Opening CODEBIN web...")
			# Open and click on "Continuar" button
			if self.webdriver == None:
				Utils.printx ("+++ Starting CODEBIN from login...")
				options = Options()
				options.add_argument("--headless")
				CodebinBot.webdriver = webdriver.Firefox (options=options)
				self.webdriver = CodebinBot.webdriver

			self.enterCodebin ()
			self.loginCodebin (pais)
			CodebinBot.IS_OPEN = True

	#-------------------------------------------------------------------
	# Codebin enter session: open URL and click into "Continuar" button
	#-------------------------------------------------------------------
	def enterCodebin (self):
		self.webdriver.get (self.url)
		#self.webdriver.get ("https://byza.corebd.net")
		submit_button = self.webdriver.find_element(By.XPATH, "//input[@type='submit']")
		submit_button.click()

		# Open new window with login form, then switch to it
		time.sleep (2)
		winMenu = self.webdriver.window_handles [-1]
		self.webdriver.switch_to.window (winMenu)

	#-------------------------------------------------------------------
	# Returns the web driver after login into CODEBIN
	#-------------------------------------------------------------------
	def loginCodebin (self, pais):
		print (f"+++ Login into CODEBIN : '{pais}'")
		# Login Form : fill user / password
		loginForm = self.webdriver.find_element (By.TAG_NAME, "form")
		userInput = loginForm.find_element (By.NAME, "user")
		#userInput.send_keys ("GRUPO BYZA")
		userInput.send_keys (self.user)
		pswdInput = loginForm.find_element (By.NAME, "pass")
		#pswdInput.send_keys ("GrupoByza2020*")
		pswdInput.send_keys (self.password)

		# Login Form:  Select pais (Importación or Exportación : Colombia or Ecuador)
		docSelectElement = self.webdriver.find_element (By.XPATH, "//select[@id='tipodoc']")
		docSelect = Select (docSelectElement)
		docSelect.select_by_value (pais)
		submit_button = loginForm.find_element (By.XPATH, "//input[@type='submit']")
		submit_button.click()

		return self.webdriver

	#----------------------------------------------------
	# Get codebin fields : {codebinField:value}
	#----------------------------------------------------
	def getCodebinValuesFromCodebinForm (self, docForm, codigoPais, docNumber):
		fields  = self.getParamFields () 
		codebinValues = {}
		for key in fields.keys():
			codebinField = fields [key]["codebinField"]
			try:
				elem = docForm.find_element (By.NAME, codebinField)
				value = elem.get_attribute ("value")
				codebinValues [codebinField] = value
			except NoSuchElementException:
				print (f"...Elemento '{codebinField}'  no existe")
				pass

		# For MANIFIESTO: Get selected radio button 
		if self.docType == "CARTAPORTE":
			codebinValues ["nocpic"] = docNumber
		elif self.docType == "MANIFIESTO":
			codebinValues ["no"] = docNumber

			radio_group = docForm.find_elements (By.NAME, "r25")  # Assuming radio buttons have name="size"
			for radio_button in radio_group:
				codebinField = radio_button.get_attribute('id')
				if radio_button.is_selected():
					codebinValues [codebinField] = "X"
				else:
					codebinValues [codebinField] = ""

		return codebinValues

	#-------------------------------------------------------------------
	# Return settings for acceding to CODEBIN documents
	#-------------------------------------------------------------------
	def getCodebinUrlSettingsForEmpresa (self):
		prefix = None
		if self.empresa == "BYZA":
			prefix = "byza"
		elif self.empresa == "NTA":
			prefix = "nta"
		else:
			raise Exception ("Empresa desconocida")
		

		settings = {}
		if self.docType == "CARTAPORTE":
			settings ["link"]    = f"https://{prefix}.corebd.net/1.cpi/nuevo.cpi.php?modo=3&idunico=%s"
			settings ["menu"]    = "Carta Porte I"
			settings ["submenu"] = "1.cpi/lista.cpi.php?todos=todos"
			settings ["prefix"]  = "CPI"

		elif self.docType == "MANIFIESTO":
			settings ["link"]    = f"https://{prefix}.corebd.net/2.mci/nuevo.mci.php?modo=3&idunico=%s"
			settings ["menu"]    = "Manifiesto de Carga"
			settings ["submenu"] = "2.mci/lista.mci.php?todos=todos"
			settings ["prefix"]  = "MCI"
		else:
			print ("Tipo de documento no soportado:", self.docType)
		return settings


	#-------------------------------------------------------------------
	# Get a list of cartaportes from range of ids
	#-------------------------------------------------------------------
	def getValuesFromRangeCodebinCartaportes (self, pais):
		self.docType = "CARTAPORTE"
		self.loginCodebin (pais)
		linkCartaporte = "https://byza.corebd.net/1.cpi/nuevo.cpi.php?modo=3&idunico=%s"

		for docId in range (121, 7075):
			docLink = linkCartaporte % docId
			self.webdriver.get (docLink)

			docForm = self.webdriver.find_element (By.TAG_NAME, "form")
			self.createParamsFileFromCodebinForm (docForm)

	#----------------------------------------------------
	# Create params file: 
	#   {paramsField: {ecudocField, codebinField, value}}
	#----------------------------------------------------
	def createParamsFileFromCodebinForm (self, docForm):
		fields  = self.getParamFields () 
		for key in fields.keys():
			codebinField = fields [key]["codebinField"]
			try:
				elem = docForm.find_element (By.NAME, codebinField)
				fields [key]["value"] = elem.get_attribute ("value")
			except NoSuchElementException:
				#print (f"...Elemento '{codebinField}'  no existe")
				pass

		pais, codigo = "NONE", "NO" 
		textsWithCountry = [fields[x]["value"] for x in ["txt02"]]
		if any (["COLOMBIA" in x.upper() for x in textsWithCountry]):
			pais, codigo = "COLOMBIA", "CO"
		elif any (["ECUADOR" in x.upper() for x in textsWithCountry]):
			pais, codigo = "ECUADOR", "EC"
			

		fields ["txt0a"]["value"] = pais

		docNumber = f"{codigo}{fields ['numero']['value']}"
		fields ["numero"]["value"] = docNumber
		fields ["txt00"]["value"]  = docNumber
		jsonFilename = f"CPI-{self.empresa}-{docNumber}-PARAMSFIELDS.json"
		json.dump (fields, open (jsonFilename, "w"), indent=4, default=str)

	#----------------------------------------------------------------
	#-- Create CODEBIN fields from document fields using input parameters
	#-- Add three new fields: idcpic, cpicfechac, ref
	#----------------------------------------------------------------
	def getParamFields (self):
		try:
			inputsParamsFile = self.getInputParametersFile ()
			inputsParams     = ResourceLoader.loadJson ("docs", inputsParamsFile)
			fields           = {}
			for key in inputsParams:
				ecudocsField  = inputsParams [key]["ecudocsField"]
				codebinField = inputsParams [key]["codebinField"]
				fields [key] = {"ecudocsField":ecudocsField, "codebinField":codebinField, "value":""}

			if self.docType == "CARTAPORTE":
				fields ["id"]             = {"ecudocsField":"id", "codebinField":"idcpic", "value":""}
				fields ["numero"]         = {"ecudocsField":"numero", "codebinField":"nocpic", "value":""}
				fields ["fecha_creacion"] = {"ecudocsField":"fecha_creacion", "codebinField":"cpicfechac", "value":""}
				fields ["referencia"]     = {"ecudocsField": "referencia", "codebinField":"ref", "value":""}

			return fields
		except: 
			raise Exception ("Obteniendo campos de CODEBIN")

	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def getEcudocCodebinFields (self):
		try:
			inputsParamsFile = self.getInputParametersFile ()
			inputsParams     = ResourceLoader.loadJson ("docs", self.inputsParams)
			fields           = {}
			for key in inputsParams:
				ecudocsField = inputsParams [key]["ecudocsField"]
				codebinField = inputsParams [key]["codebinField"]
				if codebinField:
					fields [ecudocsField]  = {"codebinField":codebinField, "value":""}

			if self.docType == "CARTAPORTE":
				fields ["id"]             = {"codebinField":"idcpic", "value":""}
				fields ["fecha_creacion"] = {"codebinField":"cpicfechac", "value":""}
				fields ["referencia"]     = {"codebinField":"ref", "value":""}

			return fields
		except: 
			raise Exception ("Obteniendo campos de CODEBIN")

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def transmitFileToCodebin (self, codebinFieldsFile):
		docType = Utils.getDocumentTypeFromFilename (codebinFieldsFile)
		Utils.printx (f">> Transmitiendo '{docType}' a codebin")
		codebinFields = json.load (open (codebinFieldsFile))
		pais = codebinFields.pop ("pais")

		self.loginCodebin (pais)
		if docType == "CARTAPORTE":
			docFrame = self.getDocumentFrame ("frame", "Carta Porte", "1", "cpi", "nuevo")
		elif docType == "MANIFIESTO":
			docFrame = self.getDocumentFrame ("frame", "Manifiesto de Carga", "2", "mci", "nuevo")

		self.fillForm (docFrame, codebinFields)

	#-----------------------------------------------
	# Get links elements from document
	#-----------------------------------------------
	def printLinksFromDocument (self, docFrame):
		elements = docFrame.find_elements (By.XPATH, "//a")
		for elem in elements:
			print ("--", elem)
			print ("----", elem.get_attribute ("text"))

	#-------------------------------------------------------------------
	# Click "Cartaporte"|"Manifiesto" then "Nuevo" returning document frame
	#-------------------------------------------------------------------
	def getDocumentFrame (self, tagName, menuStr, optionNum, itemStr, functionStr):
		try:
			iniLink = self.webdriver.find_element (By.PARTIAL_LINK_TEXT, menuStr)
			iniLink.click()

			# Open frame
			#linkString = f"//a[contains(@href, '{optionNum}.{itemStr}/nuevo.{itemStr}.php?modo=1')]"
			#linkString = f"//a[contains(@href, '{optionNum}.{itemStr}/{functionStr}.{itemStr}.php?todos=todos')]"
			linkString = f"//a[contains(@href, '{optionNum}.{itemStr}/{functionStr}.{itemStr}.php?todos=todos')]"
			print ("-- linkString:", linkString)
			iniLink = self.webdriver.find_element (By.XPATH, linkString)
			iniLink.click()

			# Switch to the frame or window containing the <object> element
			object_frame = self.webdriver.find_element (By.TAG_NAME, "object")
			print ("-- object frame:", object_frame)
			wait = WebDriverWait (self.webdriver, 2)  # Adjust the timeout as needed
			wait.until (EC.frame_to_be_available_and_switch_to_it (object_frame))

			self.printLinksFromDocument (object_frame)
			print ("-- Waiting for form...")

			# Explicitly wait for the form to be located
			docForm = WebDriverWait(self.webdriver, 10).until(
				EC.presence_of_element_located((By.TAG_NAME, tagName))
			)

			return docForm
		except Exception as e:
			Utils.printx("No se pudo crear document nuevo en el CODEBIN")
			return None

	#-----------------------------------------------------------
	#-- Fill CODEBIN form fields with ECUDOC fields
	#-----------------------------------------------------------
	def fillForm (self, docForm, codebinFields):
		CARTAPORTE  = self.docType == "CARTAPORTE"
		MANIFIESTO  = self.docType == "MANIFIESTO"
		DECLARACION = self.docType == "DECLARACION"

		for field in codebinFields.keys():
			value = codebinFields [field]
			if not value:
				continue

			# Reception data copied to the others fields
			if CARTAPORTE and field in ["lugar2", "lugaremision"]:
				continue

			# Totals calculated automatically
			elif CARTAPORTE and field in ["totalmr", "monedat", "totalmd", "monedat2"]:
				continue

			# Radio button group
			elif MANIFIESTO and "radio" in field:
				elem = docForm.find_element (By.ID, field)
				self.wedriver.execute_script("arguments[0].click();", elem)

			# Tomados de la BD del vehículo y de la BD del conductor
			elif MANIFIESTO and field in ["a9", "a10", "a11", "a12"] and \
				field in ["a19", "a20", "a21", "a22"]:
				continue  

			# Tomados de la BD de la cartaporte
			elif MANIFIESTO and field in ["a29","a30","a31","a32a","a32b",
			                              "a33","a34a","a34b","a34c","a34d","a40"]:
				continue  

			else:
				elem = docForm.find_element (By.NAME, field)
				#elem.click ()
				elem.send_keys (value.replace ("\r\n", "\n"))

	#-----------------------------------------------------------
	#-- Get CODEBIN values from form with ECUDOC fields
	#-----------------------------------------------------------
	def getDataFromForm (self, docForm, codebinFields):
		CARTAPORTE  = self.docType == "CARTAPORTE"
		MANIFIESTO  = self.docType == "MANIFIESTO"
		DECLARACION = self.docType == "DECLARACION"

		for field in codebinFields.keys():
			value = codebinFields [field]
			if not value:
				continue

			# Reception data copied to the others fields
			if CARTAPORTE and field in ["lugar2", "lugaremision"]:
				continue

			# Totals calculated automatically
			elif CARTAPORTE and field in ["totalmr", "monedat", "totalmd", "monedat2"]:
				continue

			# Radio button group
			elif MANIFIESTO and "radio" in field:
				elem = docForm.find_element (By.ID, field)
				self.wedriver.execute_script("arguments[0].click();", elem)

			# Tomados de la BD del vehículo y de la BD del conductor
			elif MANIFIESTO and field in ["a9", "a10", "a11", "a12"] and \
				field in ["a19", "a20", "a21", "a22"]:
				continue  

			# Tomados de la BD de la cartaporte
			elif MANIFIESTO and field in ["a29","a30","a31","a32a","a32b",
			                              "a33","a34a","a34b","a34c","a34d","a40"]:
				continue  

			else:
				elem = docForm.find_element (By.NAME, field)
				#elem.click ()
				elem.send_keys (value.replace ("\r\n", "\n"))

	#-------------------------------------------------------
	#-- Return input parameters file
	#-------------------------------------------------------
	def getInputParametersFile (self):
		if self.docType == "CARTAPORTE":
			self.inputsParams = "cartaporte_input_parameters.json"
		elif self.docType == "MANIFIESTO":
			self.inputsParams = "manifiesto_input_parameters.json"
		elif self.docType == "DECLARACION":
			self.inputsParams = "declaracion_input_parameters.json"
		else:
			message= f"ERROR: Tipo de documento desconocido:", docType
			raise Exception (message)
		return self.inputsParams
	
#----------------------------------------------------------
# Remove invalid CODEBIN JSON files for cartaportes 
#----------------------------------------------------------
def cleanCodebinCartaportesFiles (inDir):
	files       = os.listdir (inDir)
	invalidDir  = f"{inDir}/invalid"
	os.system (f"mkdir {invalidDir}")
	pathFiles   = [f"{inDir}/{x}" for x in files if "invalid" not in x]
	for path in pathFiles:

		print ("-- path:", path)
		data = json.load (open (path))
		subjectFields = ["txt02", "txt03", "txt04", "txt05", "txt06", "txt07", "txt08", "txt19"]
		if any ([data [x]["value"].strip()=="" for x in subjectFields]):
			os.system (f"mv {path} {invalidDir}")

#----------------------------------------------------------------
# Needs to update parameters
# startCodebinBot
#----------------------------------------------------------------
def startCodebinBot (docType, codebinFieldsFile):
	botCodebin = CodebinBot (docType, codebinFieldsFile)
	botCodebin.transmitFileToCodebin (codebinFieldsFile)

#-----------------------------------------------------------
#-----------------------------------------------------------
class CodebinException (Exception):
	pass

class DocumentNotFoundException (CodebinException):
	pass
#-----------------------------------------------------------
# Call to main
#-----------------------------------------------------------
if __name__ == "__main__":
	main()
