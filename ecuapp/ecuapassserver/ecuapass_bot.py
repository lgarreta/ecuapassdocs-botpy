import re, os, sys, json, datetime

import pyautogui as py
import pywinauto

import keyboard as kb

import pyperclip
from pyperclip import copy as pyperclip_copy
from pyperclip import paste as pyperclip_paste

from traceback import format_exc as traceback_format_exc

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_info_cartaporte import CartaporteInfo
from ecuapassdocs.info.ecuapass_info_manifiesto import ManifiestoInfo

#----------------------------------------------------------
# Globals
#----------------------------------------------------------
win   = None	 # Global Ecuapass window  object

# Deprecated: Declared as attributes
#NORMAL_PAUSE = 0.05
#SLOW_PAUSE   = 0.1

#----------------------------------------------------------
# General Bot class with basic functions of auto completing
#----------------------------------------------------------
class EcuBot:
	# Load data, check/clear browser page
	def __init__(self, jsonFilepath, runningDir, docType):
		self.jsonFilepath = jsonFilepath   
		self.runningDir   = runningDir	   
		self.docType	  = docType
		Utils.runningDir  = runningDir

		# Last update of Ecuapass file: set codes, remove "LOW"
		if docType == "CARTAPORTE":
			ecudocInfo  = CartaporteInfo (jsonFilepath, runningDir)
		elif docType == "MANIFIESTO":
			ecudocInfo  = ManifiestoInfo (jsonFilepath, runningDir)

		# Update Ecuapass file to be transmitted to ECUAPASS
		self.fields = ecudocInfo.updateEcuapassFile (jsonFilepath)
		self.notFilledFields = []	  # List of fields not filled by the bot

		# Read settings 
		settingsPath	   = os.path.join (runningDir, "settings.txt")
		Utils.printx ("Leyendo settings desde: ", settingsPath)
		settings		   = json.load (open (settingsPath, encoding="utf-8")) 
		self.empresaName   = settings ["empresa"]
		self.NORMAL_PAUSE  = float (settings ["NORMAL_PAUSE"])
		self.SLOW_PAUSE    = float (settings ["SLOW_PAUSE"])
		self.FAST_PAUSE    = float (settings ["FAST_PAUSE"])
		py.PAUSE		   = self.NORMAL_PAUSE

		Utils.printx (">>> BOT Settings:")
		Utils.printx (f"\t>>> Empresa		: <{settings ['empresa']}>")
		Utils.printx (f"\t>>> Pausa Normal	: <{settings ['NORMAL_PAUSE']}>")
		Utils.printx (f"\t>>> Pausa Lenta	: <{settings ['SLOW_PAUSE']}>")
		Utils.printx (f"\t>>> Pausa Rápida	: <{settings ['FAST_PAUSE']}>")

	#-------------------------------------------------------------------
	# Executes general bot procedure
	#-------------------------------------------------------------------
	def start (self):
		message = ""
		try:
			Utils.printx (f"Iniciando digitaciOn de documento '{self.jsonFilepath}'")
			self.initEcuapassWindow ()
			py.sleep (0.2)
			self.fillEcuapass ()
			message = Utils.printx (f"MENSAJE: Documento digitado correctamente")
		except Exception as ex:
			text = str (ex).strip (")(") 
			message = Utils.printx (f"ALERTA: {text}")
			Utils.printException (message)

		return (message)

	#-- Check/init Ecuapass window
	def initEcuapassWindow (self):
		Utils.printx ("Iniciando ventana de ECUAPASS...")
		
		self.win = self.activateEcuapassWindow ()
		#py.sleep (0.2)
		#self.maximizeWindow (self.win)
		#py.sleep (0.2)
		#self.scrollWindowToBeginning ()

		self.detectEcuapassDocumentPage (self.docType)
		self.clearWebpageContent ()

	#-- Select first item from combo box
	def selFirstItemFromBox  (self):
		py.press ("down")
		py.press ("enter")

	#--------------------------------------------------------------------
	# Detect if is on find button using image icon
	#--------------------------------------------------------------------
	def isOnFindButton (self):
		Utils.printx ("Localizando botón de búsqueda...")
		filePaths = Utils.imagePath ("image-button-FindRUC")
		for fpath in filePaths:
			Utils.printx ("...Probando: ", os.path.basename (fpath))
			xy = py.locateCenterOnScreen (fpath, confidence=0.90, grayscale=False)
			if (xy):
				print ("...Detectado:", fpath)
				return True
	#--------------------------------------------------------------------
	# Check for error message box 'Seleccion Nula" 
	#--------------------------------------------------------------------
	def checkErrorDialogBox (self, imageName):
		Utils.printx (f"Verificando '{imageName}'...")
		filePaths = Utils.imagePath (imageName)
		for fpath in filePaths:
			Utils.printx (">>> Buscando la imágen: ", os.path.basename (fpath))
			xy = py.locateCenterOnScreen (fpath, confidence=0.80, grayscale=False)
			print ("--xy:", xy)
			if (xy):
				raise Exception (f"Se presentó errores en '{imageName}'")

	#--------------------------------------------------------------------
	# Fill subject fields waiting for RUC info for ecuadorian companies
	#--------------------------------------------------------------------

	def fillSubject (self, subjectType, fieldProcedimiento, fieldPais, fieldTipoId, 
					 fieldNumeroId, fieldNombre, fieldDireccion, fieldCertificado=None):
		#---------------- fill data about subject -------------------
		def processEcuapassId (fieldTipoId, fieldNumeroId):
			newType, newNumber = None, None
			if self.fields [fieldTipoId] == "NIT":
				self.fields [fieldTipoId]   = "OTROS"
				self.fields [fieldNumeroId] = self.fields [fieldNumeroId].split ("-")[0]

		def fillData (fieldPais, fieldTipoId, fieldNumeroId):
			self.fillBoxCheck (fieldPais)
			processEcuapassId (fieldTipoId, fieldNumeroId)
			self.fillBoxCheck (fieldTipoId)
			self.fillText (fieldNumeroId)
		#------------------------------------------------------------
		procedimiento = self.fields [fieldProcedimiento]
		Utils.printx (f"Procedimiento: '{procedimiento}', Sujeto: '{subjectType}'")
		fillData (fieldPais, fieldTipoId, fieldNumeroId); py.sleep (0.01)
		if	("EXPORTACION" in procedimiento and subjectType == "REMITENTE") or \
			("IMPORTACION" in procedimiento and subjectType != "REMITENTE"):
			Utils.printx ("Es una empresa ecuatoriana, verificando RUC")
			nTries = 0
			while not self.isOnFindButton () and nTries < 5:
				Utils.printx ("...Esperando botón de búsqueda")
				self.skipN (3, "LEFT"); py.sleep (self.SLOW_PAUSE)	# Regresa para que se active el boton de "find" 
				fillData (fieldPais, fieldTipoId, fieldNumeroId); py.sleep (0.01)
				nTries += 1

			if nTries == 5:
				raise Exception (f"ECUAPASS no pudo sincronizar datos de '{subjectType}'")

			py.press ("space"); 
			py.sleep (2)
		else:
			Utils.printx ("No es una empresa ecuatoriana, no verifica RUC")
			if subjectType == "REMITENTE":
				self.fillText (fieldCertificado)
			self.fillText (fieldNombre)

		self.fillText (fieldDireccion)

	#--------------------------------------------------------------------
	# Fill one of three radio buttons (PO, CI, PEOTP) according to input info
	#--------------------------------------------------------------------
	def fillRButton (self, fieldName):
		value = self.fields [fieldName]
		if (value == "1"):
			py.press ("Tab")
		else:
			py.press ("right")

	#--------------------------------------------------------------------
	#-- fill text field
	#--------------------------------------------------------------------
	def fillText (self, fieldName, TAB_FLAG="TAB"):
		py.PAUSE = self.FAST_PAUSE

		value = self.fields [fieldName]
		Utils.printx (f"Llenando TextField '{fieldName}' : '{value}'...")
		if value != None:
			pyperclip_copy (value)
			py.hotkey ("ctrl", "v")
			py.sleep (self.SLOW_PAUSE)

		if TAB_FLAG == "TAB":
			py.press ("Tab")

		py.PAUSE = self.NORMAL_PAUSE

	#--------------------------------------------------------------------
	#-- Fill combo box pasting text and selecting first value.
	#-- Without check. Default value, if not found. 
	#-- Using keyboard library instead pyautogui
	#--------------------------------------------------------------------
	def fillBox (self, fieldName, TAB_FLAG="TAB"):
		py.PAUSE = self.FAST_PAUSE

		fieldValue = self.fields [fieldName]
		Utils.printx (f"Llenando CombolBox '{fieldName}' : '{fieldValue}'...")
		if fieldValue == None:
			return

		pyperclip_copy (fieldValue)
		py.hotkey ("ctrl", "v")
		py.sleep (self.SLOW_PAUSE)
		py.press ("down")
		py.sleep (self.SLOW_PAUSE)

		if TAB_FLAG == "TAB":
			py.press ("Tab")

		py.PAUSE = self.NORMAL_PAUSE

	#--------------------------------------------------------------------
	# Select value in combo box by pasting, checking, and pasting
	# Return true if selected, raise an exception in other case.
	#--------------------------------------------------------------------
	def fillBoxCheck (self, fieldName, TAB_FLAG="TAB_CHECK"):
		try:
			fieldValue = self.fields [fieldName]
			Utils.printx (f"Llenando ComboBox '{fieldName}' : '{fieldValue}'...")
			if fieldValue == None:
				py.press ("Enter") if "NOTAB" in TAB_FLAG else py.press ("Tab")
				return True

			py.PAUSE = self.NORMAL_PAUSE
			for i in range (10):
				pyperclip_copy (fieldValue)
				py.hotkey ("ctrl", "v"); py.sleep (0.05);py.press ("down"); 
				pyperclip_copy ("")

				py.hotkey ("ctrl","c"); 
				text = pyperclip_paste().lower()
				Utils.printx (f"...Intento {i}: Buscando '{fieldValue}' en texto '{text}'")

				if fieldValue.lower() in text.lower():
					py.PAUSE = 0.3
					pyperclip_copy (fieldValue)
					py.hotkey ("ctrl", "v"); py.press ("enter"); py.sleep (0.01)
					#py.hotkey ("ctrl", "v"); 
					py.PAUSE = self.NORMAL_PAUSE

					#py.press ("TAB") if TAB_FLAG == "TAB" else py.press ("Enter")
					py.press ("Enter") if "NOTAB" in TAB_FLAG else py.press ("Tab")

					Utils.printx (f"...Encontrado '{fieldValue}' en '{text}'")
					return True
				else:
					py.PAUSE += 0.01

				py.hotkey ("ctrl", "a"); py.press ("backspace");

			# Check or not check
			if "NOCHECK" in TAB_FLAG:
				return True
			else:
				message = f"Problemas en el ECUAPASS sincronizando '{fieldName}':'{fieldValue}'"
				raise Exception (message)
		finally:
			py.PAUSE = self.NORMAL_PAUSE
			
	#--------------------------------------------------------------------
	# Skip N cells forward or backward 
	#--------------------------------------------------------------------
	def skipN (self, N, direction="RIGHT"):
		py.PAUSE = self.FAST_PAUSE

		if direction == "RIGHT":
			[py.press ("Tab") for i in range (N)]
		elif direction == "LEFT":
			[py.hotkey ("shift", "Tab") for i in range (N)]
		else:
			print (f"Direccion '{direction}' desconocida ")

		py.PAUSE = self.NORMAL_PAUSE

	#------------------------------------------------------------------
	#-- Fill box iterating, copying, comparing.
	#------------------------------------------------------------------
	def fillBoxIter (self, fieldValue, TAB_FLAG="TAB"):
		py.PAUSE = self.NORMAL_PAUSE
		fieldValue = fieldValue.upper ()
		Utils.printx (f"Buscando '{fieldValue}'...")

		for i in range (10):
			lastText = ""
			py.press ("home")
			while True:
				py.press ("down"); py.sleep (0.1)
				py.hotkey ("ctrl", "a", "c"); py.sleep (0.1)
				text = pyperclip_paste().upper()
				if fieldValue in text:
					Utils.printx (f"...Intento {i}: Encontrado {fieldValue} en {text}") 
					[py.press ("Tab") if TAB_FLAG=="TAB" else py.press ("enter")] 
					return

				if (text == lastText):
					Utils.printx (f"...Intento {i}: Buscando '{fieldValue}' en {text}")
					break
				lastText = text 
			py.sleep (0.2)

		Utils.printx (f"...No se pudo encontrar '{fieldValue}'")
		py.PAUSE = self.NORMAL_PAUSE
		if TAB_FLAG == "TAB":
			py.press ("Tab")

	#-------------------------------------------------------------------
	#-- Fill Date box widget (month, year, day)
	#-------------------------------------------------------------------
	def fillDate (self, fieldName, GET=True):
		py.PAUSE = self.NORMAL_PAUSE
		try:
			Utils.printx (f"Llenando campo Fecha '{fieldName}' : {self.fields [fieldName]}'...")
			fechaText = self.fields [fieldName]
			if (fechaText == None):
				return

			items = fechaText.split("-")
			day, month, year = int (items[0]), int (items[1]), int (items[2])

			currentDate = datetime.datetime.now ()
			if GET:
				currentDate  = self.getBoxDate ()

			dayBox		= currentDate.day
			monthBox	= currentDate.month
			yearBox		= currentDate.year
			Utils.printx (f"...Fecha actual: {dayBox}-{monthBox}-{yearBox}. Full: ", currentDate)

			py.hotkey ("ctrl", "down")
			#py.PAUSE = self.FAST_PAUSE
			self.setYear  (year, yearBox)
			self.setMonth (month, monthBox)
			self.setDay (day)
			#py.PAUSE = self.NORMAL_PAUSE
		except Exception as ex:
			Utils.printException ("FECHA:")
			raise Exception ("No se pudo establecer fecha. \n" + str (ex)) 

	#-- Set year
	def setYear (self, yearDoc, yearOCR):
		diff = yearDoc - yearOCR
		pageKey = "pageup" if diff < 0 else "pagedown"
		pageSign = "-" if diff < 0 else "+"

		for i in range (abs(diff)):
			py.hotkey ("shift", pageSign)

	#-- Set month
	def setMonth (self, monthDoc, monthOCR):											 
		diff = monthDoc - monthOCR
		pageKey = "pageup" if diff < 0 else "pagedown"

		for i in range (abs(diff)):
			py.press (pageKey)

	#-- Set day
	def setDay (self, dayDoc):
			nWeeks = dayDoc // 7
			nDays  = dayDoc % 7 - 1

			py.press ("home")
			[py.press ("down") for i in range (nWeeks)]
			[py.press ("right") for i in range (nDays)]

			py.press ("enter")

	#-- Get current date fron date box widget
	def getBoxDate (self):
		count = 0
		while True:
			count += 1
			py.hotkey ("ctrl", "down")
			py.press ("home")
			py.hotkey ("ctrl", "a")
			py.hotkey ("ctrl", "c")
			text	 = pyperclip_paste ()

			reFecha = r'\d{1,2}/\d{1,2}/\d{4}'
			if re.match (reFecha, text):
				boxDate  = text.split ("/") 
				boxDate  = [int (x) for x in boxDate]
				class BoxDate:
					day = boxDate[0]; month = boxDate [1]; year = boxDate [2]
				return (BoxDate())

			if (count > 112):
				raise Exception ("Sobrepasado el número de dias al buscar fecha.")

	#----------------------------------------------------------------
	#-- Function for windows management
	#----------------------------------------------------------------
	#-- Detect ECUAPASS window
	def detectWindowByTitle (self, titleString):
		Utils.printx (f"Detectando ventana '{titleString}'...")
		windows = py.getAllWindows ()
		for win in windows:
			if titleString in win.title:
				return win

		raise Exception (f"No se detectó ventana '{titleString}' ")

	#-- Maximize window by minimizing and maximizing
	def maximizeWindow (self, win):
		SLEEP=0.3
		py.PAUSE = self.SLOW_PAUSE
		win.minimize (); py.sleep (SLEEP)
		win.restore (); py.sleep (0.1)
		py.hotkey ("win", "up")
		py.PAUSE = self.NORMAL_PAUSE
		#win.activate (); #py.sleep (SLEEP)
		#win.resizeTo (py.size()[0], py.size()[1]); py.sleep (SLEEP)

	def activateWindowByTitle (self, titleString):
		SLEEP=0.2
		ecuWin = self.detectWindowByTitle (titleString)
		Utils.printx (f"Activando ventana '{titleString}'...", ecuWin)
		
		#ecuWin.activate (); py.sleep (SLEEP)
		if ecuWin.isMinimized:
			ecuWin.activate (); py.sleep (SLEEP)

		return (ecuWin)

	#-- Detect and activate ECUAPASS-browser/ECUAPASS-DOCS window
	def activateEcuapassWindow (self):
		try:
			Utils.printx ("Activando la ventana del ECUAPASS...")
			ecuapassTitle = 'ECUAPASS - SENAE browser'
			#return self.activateWindowByTitle ('ECUAPASS - SENAE browser')

			# Connect to an existing instance of an application by its title
			app = pywinauto.Application().connect(title=ecuapassTitle)

			# Get a reference to the main window and activate it
			ecuapass_window = app.window(title=ecuapassTitle)
			ecuapass_window.set_focus()
		except pywinauto.ElementNotFoundError:
			raise Exception (f"No está abierta la ventana del ECUAPASS")

	def activateEcuapassDocsWindow (self):
		return self.activateWindowByTitle ('Ecuapass-Docs')

	#-- Clear previous webpage content clicking on "ClearPage" button
	def clearWebpageContent (self):
		Utils.printx ("Localizando botón de borrado...")
		filePaths = Utils.imagePath ("image-button-ClearPage")
		for fpath in filePaths:
			print (">>> Probando: ", os.path.basename (fpath))
			xy = py.locateCenterOnScreen (fpath, confidence=0.80, grayscale=True)
			if (xy):
				print (">>> Detectado")
				py.click (xy[0], xy[1], interval=1)    
				return True

		raise Exception ("No se detectó botón de borrado")
		
	#-- Scroll to the page beginning 
	def scrollWindowToBeginning (self):
		Utils.printx ("Desplazando página hasta el inicio...")
		filePaths = Utils.imagePath ("image-button-ScrollUp")
		for fpath in filePaths:
			print (">>> Probando: ", os.path.basename (fpath))
			xy = py.locateCenterOnScreen (fpath, confidence=0.80, grayscale=True)
			if (xy):
				print (">>> Detectado")
				py.mouseDown (xy[0], xy[1])
				py.sleep (1)
				py.mouseUp (xy[0], xy[1])
				return True

		raise Exception ("No se pudo desplazar la página ECUAPASS al inicio")

	#-- Scroll down/up N times (30 pixels each scroll)
	def scrollN (self, N, direction="down"):
		py.PAUSE = self.NORMAL_PAUSE
		sizeScroll = -10000 if direction=="down" else 10000
		#Utils.printx (f"\tScrolling {sizeScroll} by {N} times...")
		for i in range (N):
			#Utils.printx (f"\t\tScrolling {i} : {30*i}")
			py.scroll (sizeScroll)

	#-- Check if active webpage contains correct text 
	def detectEcuapassDocumentPage (self, docType):
		Utils.printx (f"Detectando página de '{docType}' activa...")
		docFilename = "";
		if docType == "CARTAPORTE":
			docFilename = "image-text-Cartaporte"; 
		elif docType == "MANIFIESTO":
			docFilename = "image-text-Manifiesto"; 
		elif docType == "DECLARACION":
			docFilename = "image-text-DeclaracionTransito.png"; 

		filePaths = Utils.imagePath (docFilename)
		for fpath in filePaths:
			print (">>> Probando: ", os.path.basename (fpath))
			xy = py.locateCenterOnScreen (fpath, confidence=0.80, grayscale=True)
			if (xy):
				print (">>> Detectado")
				return True

		message = f"No se detectó la página de '{docType}'"
		raise Exception (message)

	#-- Click on selected cartaporte
	def clickSelectedCartaporte (self, fieldName):
		Utils.printx ("Localizando cartaporte...")
		xy = py.locateCenterOnScreen (Utils.imagePath ("image-text-blue-TERRESTRE-manifiesto.png"), 
				confidence=0.7, grayscale=False)
		if (xy):
			print (">>> Cartaporte detectada")
			py.click (xy[0], xy[1], interval=1)    
			return True

		fieldValue = self.fields [fieldName]
		self.notFilledFields.append ((fieldName, fieldValue))
		Utils.printx ("ALERTA: No se detectó cartaporte seleccionada")

	#-- Create message with fields not filled
	def createResultsMessage (self):
		msgs = [f"ALERTA: Finalizada la digitación"]
		if self.notFilledFields != []:
			msgs.append ("Los siguientes campos no se pudieron llenar:")
			for field in self.notFilledFields:
				msgs.append (f"{field [0]} : {field [1]}")

		message = "\\".join (msgs)
		return (message)

if __name__ == "__main__":
	main()
