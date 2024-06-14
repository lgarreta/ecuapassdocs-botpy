
import os, time
import pyautogui as py
from pyperclip import copy as pyperclip_copy
from pyperclip import paste as pyperclip_paste
from traceback import format_exc as traceback_format_exc
from ecuapass_utils import Utils

#----------------------------------------------------------
# Globals
#----------------------------------------------------------
win   = None	 # Global Ecuapass window  object
PAUSE = 0

#----------------------------------------------------------
# Main function for testing
#----------------------------------------------------------
def mainBot (jsonFilepath, temporalDir):
	Utils.printx (f"Versión0.85. Iniciando ingreso de documento '{jsonFilepath}'")
	Utils.printx (f"Directorio actual: ", os.getcwd())
	Utils.temporalDir = temporalDir
	result = EcuBot.fillEcuapass (jsonFilepath)
	return result

#--------------------------------------------------------------------
# EcuBot for filling Ecuapass cartaporte web form (in flash)
#--------------------------------------------------------------------
class EcuBot:
	#-- Main function for testing
	def fillEcuapass (jsonFilepath):
		py.sleep (1)
		Utils.printx (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<")
		try:
			global win
			fieldsConfidence = Utils.readJsonFile (jsonFilepath)
			fields = EcuBot.removeConfidenceString (fieldsConfidence)
			
			win    = Utils.detectEcuapassWindow ()
			Utils.printx (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<")
			Utils.checkCPITWebpage ()
			Utils.clearWebpageContent ()
			py.press ("Tab"); py.press ("Tab")

			# Encabezado
			time.sleep (PAUSE)
			EcuBot.fillBoxSimpleIteration (fields, "01_Distrito"); py.press ("Tab")
			EcuBot.fillText (fields, "02_NumeroCPIC"); py.press ("Tab")
			EcuBot.fillText (fields, "03_MRN"); py.press ("Tab"); 
			EcuBot.fillText (fields, "04_MSN"); py.press ("Tab")
			EcuBot.fillBox (fields, "05_TipoProcedimiento"); py.press ("Tab")
			#EcuBot.fillTextSelection (fields, "06_EmpresaTransporte") # Selected by default
			py.press ("Tab")
			EcuBot.fillBox (fields, "07_DepositoMercancia"); py.press ("Tab")

			EcuBot.fillText (fields, "08_DirTransportista"); py.press ("Tab");
			EcuBot.fillText (fields, "09_NroIdentificacion"); py.press ("Tab")

			Utils.scrollN (5)

			# Remitente
			time.sleep (PAUSE)
			EcuBot.fillBox (fields, "10_PaisRemitente"); py.press ("Tab")
			EcuBot.fillBox (fields, "11_TipoIdRemitente") ; py.press ("Tab")
			EcuBot.fillText (fields, "12_NroIdRemitente"); py.press ("Tab")
			EcuBot.fillText (fields, "13_NroCertSanitario"); py.press ("Tab")
			EcuBot.fillBox (fields, "14_NombreRemitente"); py.press ("Tab")
			EcuBot.fillText (fields, "15_DireccionRemitente"); py.press ("Tab")


			# Destinatario
			time.sleep (PAUSE)
			EcuBot.fillTextSelection (fields, "16_PaisDestinatario"); py.press ("Tab")
			EcuBot.fillTextSelection (fields, "17_TipoIdDestinatario"); py.press ("Tab")
			EcuBot.fillText (fields, "18_NroIdDestinatario"); py.press ("Tab")
			py.press ("Tab")   # Skip Boton buscar
			EcuBot.fillTextSelection (fields, "19_NombreDestinatario"); py.press ("Tab")
			EcuBot.fillText (fields, "20_DireccionDestinatario"); py.press ("Tab")


			# Consignatario
			time.sleep (PAUSE)
			EcuBot.fillBox (fields, "21_PaisConsignatario"); py.press ("Tab")
			EcuBot.fillBox (fields, "22_TipoIdConsignatario"); py.press ("Tab")
			EcuBot.fillText (fields, "23_NroIdConsignatario"); py.press ("Tab")
			py.press ("Tab")    # Boton buscar consignatario por Id
			EcuBot.fillText (fields, "24_NombreConsignatario"); py.press ("Tab")
			EcuBot.fillText (fields, "25_DireccionConsignatario"); py.press ("Tab")

			Utils.scrollN (10)

			# Notificado
			time.sleep (PAUSE)
			EcuBot.fillText (fields, "26_NombreNotificado"); py.press ("Tab")
			EcuBot.fillText (fields, "27_DireccionNotificado"); py.press ("Tab")
			EcuBot.fillBox (fields, "28_PaisNotificado"); py.press ("Tab")

			# Paises: Recepcion, Embarque, Entrega
			#time.sleep (PAUSE)
			Utils.scrollN (10)
			EcuBot.fillBox (fields, "29_PaisRecepcion"); 
			py.press ("Tab"); py.press ("Tab"); py.press ("Tab")
			EcuBot.fillBox (fields, "32_PaisEmbarque"); 
			py.press ("Tab"); py.press ("Tab"); py.press ("Tab")
			EcuBot.fillBox (fields, "35_PaisEntrega"); 

			# Pais INCOTERM
			time.sleep (PAUSE)
			[py.press ("Tab") for i in range (13)]
			EcuBot.fillBox (fields, "48_PaisMercancia"); 

			# Pais Emision
			time.sleep (PAUSE)
			[py.press ("Tab") for i in range (14)]
			EcuBot.fillBox (fields, "62_PaisEmision"); 

			[py.hotkey ("shift", "Tab") for i in range (32)]

			# Fechas: Recepcion, Embarque, Entrega
			time.sleep (PAUSE)
			EcuBot.fillBox (fields, "30_CiudadRecepcion"); py.press ("Tab")
			EcuBot.fillFecha (fields, "31_FechaRecepcion"); 
			py.press ("Tab"); py.press ("Tab"); 

			EcuBot.fillBox (fields, "33_CiudadEmbarque"); py.press ("Tab")
			EcuBot.fillFecha (fields, "34_FechaEmbarque"); 
			py.press ("Tab"); py.press ("Tab"); 
			EcuBot.fillBox (fields, "36_CiudadEntrega"); py.press ("Tab")
			EcuBot.fillFecha (fields, "37_FechaEntrega"); py.press ("Tab") 

			#Utils.scrollN (5)

			# Condiciones
			time.sleep (PAUSE)
			EcuBot.fillCondicionesTransporte (fields, "38_CondicionesTransporte"); py.press ("Tab")
			EcuBot.fillCondicionesPago (fields, "39_CondicionesPago"); py.press ("Tab")

			# Mercancia
			time.sleep (PAUSE)
			EcuBot.fillText (fields, "40_PesoNeto"); py.press ("Tab")
			EcuBot.fillText (fields, "41_PesoBruto"); py.press ("Tab")
			EcuBot.fillText (fields, "42_TotalBultos"); py.press ("Tab")
			EcuBot.fillText (fields, "43_Volumen"); py.press ("Tab")
			EcuBot.fillText (fields, "44_OtraUnidad"); py.press ("Tab")
			EcuBot.fillText (fields, "45_PrecioMercancias"); py.press ("Tab")

			# INCOTERM
			time.sleep (PAUSE)
			EcuBot.fillBox (fields, "46_INCOTERM"); py.press ("Tab")
			EcuBot.fillBox (fields, "47_TipoMoneda"); py.press ("Tab")
			py.press ("Tab")
			EcuBot.fillBox (fields, "49_CiudadMercancia"); py.press ("Tab")

			Utils.scrollN (5)

			# Gastos
			time.sleep (PAUSE)
			EcuBot.fillText (fields, "50_GastosRemitente"); py.press ("Tab")
			EcuBot.fillBox (fields, "51_MonedaRemitente"); py.press ("Tab")
			EcuBot.fillText (fields, "52_GastosDestinatario"); py.press ("Tab")
			EcuBot.fillBox (fields, "53_MonedaDestinatario"); py.press ("Tab")
			EcuBot.fillText (fields, "54_OtrosGastosRemitente"); py.press ("Tab")
			EcuBot.fillBox (fields, "55_OtrosMonedaRemitente"); py.press ("Tab")
			EcuBot.fillText (fields, "56_OtrosGastosDestinatario"); py.press ("Tab")
			EcuBot.fillBox (fields, "57_OtrosMonedaDestinataio"); py.press ("Tab")
			EcuBot.fillText (fields, "58_TotalRemitente"); py.press ("Tab")
			EcuBot.fillText (fields, "59_TotalDestinatario"); py.press ("Tab")

			Utils.scrollN (5)

			# Documentos
			EcuBot.fillText (fields, "60_DocsRemitente"); py.press ("Tab")

			# Emision
			EcuBot.fillFecha (fields, "61_FechaEmision"); py.press ("Tab")
			py.press ("Tab")
			EcuBot.fillBox (fields, "63_CiudadEmision"); py.press ("Tab")

			# Instrucciones
			EcuBot.fillText (fields, "64_Instrucciones"); py.press ("Tab")
			EcuBot.fillText (fields, "65_Observaciones"); py.press ("Tab")

			[py.press ("Tab") for i in range (3)]

			Utils.scrollN (10)
			# Detalles
			time.sleep (PAUSE)
			EcuBot.fillText (fields, "66_Secuencia"); py.press ("Tab")
			EcuBot.fillText (fields, "67_CantidadBultos"); py.press ("Tab")
			EcuBot.fillTipoEmbalaje (fields, "68_TipoEmbalaje"); py.press ("Tab")
			EcuBot.fillText (fields, "69_MarcasNumeros"); py.press ("Tab")
			EcuBot.fillText (fields, "70_PesoNeto"); py.press ("Tab")
			EcuBot.fillText (fields, "71_PesoBruto"); py.press ("Tab")
			EcuBot.fillText (fields, "72_Volumen"); py.press ("Tab")
			EcuBot.fillText (fields, "73_OtraUnidad"); py.press ("Tab")

			# IMOs
			time.sleep (PAUSE)
			EcuBot.fillText (fields, "74_Subpartida"); py.press ("Tab"); py.press ("Tab")
			EcuBot.fillBox (fields, "75_IMO1"); py.press ("Tab")
			EcuBot.fillBox (fields, "76_IMO2"); py.press ("Tab")
			EcuBot.fillBox (fields, "77_IMO2"); py.press ("Tab")
			EcuBot.fillText (fields, "78_NroCertSanitario"); py.press ("Tab")
			EcuBot.fillText (fields, "79_DescripcionCarga"); py.press ("Tab")
		except Exception as ex:
			Utils.printx (f"EXCEPCION: Problemas al llenar documento '{jsonFilepath}'")
			print (traceback_format_exc())
			return (str(ex))

		return (f"Ingresado exitosamente el documento {jsonFilepath}")

    #-- Remove text added with confidence value ("wwww||dd")
	def removeConfidenceString (fieldsConfidence):
		fields = {}
		for k in fieldsConfidence:
			fields [k] = None if fieldsConfidence [k] == None else fieldsConfidence [k].split ("||")[0]
		return fields

	#--------------------------------------------------------------------
	# Special fields
	#--------------------------------------------------------------------
	#-- Fill '68 Tipo Embalaje' combo box
	def fillTipoEmbalaje (fields, fieldName):
		value = fields [fieldName].upper()
		if value.upper() in ["ESTIBA", "PALLETS"]:
			value = "PALLETES"

		fields [fieldName] = value
		EcuBot.fillBox (fields, fieldName)


	#-- Fill '38 Condiciones Transporte' combo box
	def fillCondicionesTransporte (fields, fieldName):
		value = fields [fieldName].upper()
		if "DIRECTO" in value and "SIN" in value:
			text = "DIRECTO, SIN CAMBIO DEL CAMION"
		elif "DIRECTO" in value and "CON" in value:
			text = "DIRECTO, CON CAMBIO DEL TRACTO-CAMION"
		elif "TRANSBORDO" in value:
			text = "TRANSBORDO"

		fields [fieldName] = text
		EcuBot.fillBox (fields, fieldName)
		
	#-- 39_CondicionesPago
	def fillCondicionesPago (fields, fieldName):
		value = fields [fieldName].upper()
		if "CREDITO" in value: 
			text = "POR COBRAR"
		else: 
			text = value
			#text = "--Selección--"

		fields [fieldName] = text
		EcuBot.fillBox (fields, fieldName)

	#--------------------------------------------------------------------
	# Filling doc fields
	#--------------------------------------------------------------------
	#-- Fill combo box pasting text and selecting first value.
	#-- Without check. Default value, if not found.
	def fillBox (fields, fieldName):
		#py.pause = 0.01
		value = fields [fieldName]
		if value == None:
			return
		# Copy field text
		fieldText = value.upper()
		pyperclip_copy (fieldText)
		py.hotkey ("ctrl", "v")
		py.press ("down")

		# Check if selection is null
		py.hotkey ("ctrl", "c")
		if pyperclip_paste () == fieldText:
			Utils.printx (f"No se encontró la opción '{fieldText}' en el campo '{fieldName}'")
			py.press ("--")
		else:
			pyperclip_copy (fieldText)
			py.hotkey ("ctrl", "v")

		py.press ("down")
		py.press ("enter")

	#-- Fill box iterating, copying, comparing.
	def fillBoxSimpleIteration (fields, fieldName):
		fieldText = fields [fieldName].upper()
		Utils.printx (f"> >> Llenando simple CBox '{fieldName} : {fieldText}'...")

		lastText = "XXXYYYZZZ"
		while True:
			py.hotkey ("ctrl", "a");py.hotkey ("ctrl","c"); 
			text = pyperclip_paste().upper()
			if fieldText in text:
				Utils.printx (f"\t\t Encontrado {fieldText} en {text}") 
				py.press ("enter"); 
				break

			if (text == lastText):
				Utils.printx (f"\t\t No se pudo encontrar '{fieldText}'!")
				break

			py.press ("down");
			lastText = text 

	#-- fill text field with selection
	def fillTextSelection (fields, fieldName, imageName=None):
		EcuBot.fillText (fields, fieldName, imageName)
		py.press ("Enter")


	#-- fill text field
	def fillText (fields, fieldName, imageName=None):
		value = fields [fieldName]
		Utils.printx (f"Llenando TextField '{fieldName}' : '{value}'...")
		if value == None:
			return

		pyperclip_copy (value)
		if imageName == None:
			#py.write (value)
			py.hotkey ("ctrl", "v")


	#-- fill combo box iterating over all values (Ctrl+x+v+a+back)
	def fillCBoxFieldByIterating (fields, fieldName):
		fieldText = fields [fieldName].lower()
		Utils.printx (f"> >> Llenando CBox iterando uno a uno '{fieldName} : {fieldText}'...")

		py.hotkey ("ctrl","c"); py.hotkey ("ctrl","v"); py.hotkey ("ctrl","a");
		py.press ("backspace");
		py.press ("down");

		lastText = "XXXYYYZZZ"
		while True:
			py.hotkey ("ctrl","c"); py.hotkey ("ctrl","v")
			text = pyperclip_paste().lower()
			value = Utils.strCompare (fieldText, text) 
			Utils.printx (f"\t\t Comparando texto campo '{fieldText}' con texto CBox '{text}', valor: {value}")
			#if value > 0.8:
			if fieldText in text:
				Utils.printx (f"\t\t Encontrado!") 
				py.press ("enter"); py.press ("enter")
				break

			if (text == lastText):
				Utils.printx (f"\t\tERROR: No se pudo encontrar '{fieldText}'!")
				break

			py.hotkey ("ctrl","a"); py.press ("backspace"); py.press ("down");
			lastText = text 


	#-- Fill Date box widget (month, year, day)
	def fillFecha (fields, fieldName):
		Utils.printx (f"Llenando campa Fecha '{fieldName}' : {fields [fieldName]}'...")
		fechaText = fields [fieldName]
		if (fechaText == None):
			return

		items = fechaText.split("-")
		day, month, year = int (items[0]), int (items[1]), int (items[2])

		boxDate    = EcuBot.getBoxDate ()
		dayBox	   = boxDate [0]
		monthBox   = boxDate [1]
		yearBox    = boxDate [2]

		py.hotkey ("ctrl", "down")
		EcuBot.setYear  (year, yearBox)
		EcuBot.setMonth (month, monthBox)
		EcuBot.setDay (day)

	#-- Get current date fron date box widget
	def getBoxDate ():
		py.hotkey ("ctrl", "down")
		py.press ("home")
		py.hotkey ("ctrl", "a")
		py.hotkey ("ctrl", "c")
		text	 = pyperclip_paste ()
		boxDate  = text.split ("/") 
		boxDate  = [int (x) for x in boxDate]
		return (boxDate)

	#-- Set year
	def setYear (yearDoc, yearOCR):
		diff = yearDoc - yearOCR
		pageKey = "pageup" if diff < 0 else "pagedown"
		Utils.printx (f"Localizando año. Doc: {yearDoc}. OCR: {yearOCR}. Diff: {diff}...")

		for i in range (abs(diff)):
			Utils.printx (f"Año %.2d: " % (i+1), end="")
			for k in range (12):
				Utils.printx (f">%.2d " % (k+1), end="")
				py.press (pageKey)
			Utils.printx ("")
		Utils.printx ("")

	#-- Set month
	def setMonth (monthDoc, monthOCR):											 
		diff = monthDoc - monthOCR
		pageKey = "pageup" if diff < 0 else "pagedown"
		Utils.printx (f"Localizando mes. Doc: {monthDoc}. OCR: {monthOCR}. Diff: {diff}...")

		for i in range (abs(diff)):
			Utils.printx (f"> %.2d " % (i+1), end="")
			py.press (pageKey)

	#-- Set day
	def setDay (dayDoc):
		try:
			nWeeks = dayDoc // 7
			nDays  = dayDoc % 7 - 1
			Utils.printx (f"Localizando dia {dayDoc}. Semanas: {nWeeks}, Dias: {nDays}...")

			py.press ("home")
			[py.press ("down") for i in range (nWeeks)]
			[py.press ("right") for i in range (nDays)]

			py.press ("enter")
		except:
			Utils.printx (f"EXCEPTION: Al buscar el dia '{dayDoc}'")
			raise

