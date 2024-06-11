#!/usr/bin/env python3

import os, sys, json, re, time
import PyPDF2

from pickle import load as pickle_load
from pickle import dump as pickle_dump
from traceback import format_exc as traceback_format_exc

from ecuapassdocs.info.ecuapass_info_cartaporte_BYZA import CartaporteByza
from ecuapassdocs.info.ecuapass_info_cartaporte_BOTERO import CartaporteBotero
from ecuapassdocs.info.ecuapass_info_cartaporte_NTA import CartaporteNTA
from ecuapassdocs.info.ecuapass_info_cartaporte_SYTSA import CartaporteSytsa
from ecuapassdocs.info.ecuapass_info_manifiesto_BYZA import ManifiestoByza
from ecuapassdocs.info.ecuapass_info_manifiesto_BOTERO import ManifiestoBotero
from ecuapassdocs.info.ecuapass_info_manifiesto_NTA import ManifiestoNTA
from ecuapassdocs.info.ecuapass_info_manifiesto_SYTSA import ManifiestoSytsa
from ecuapassdocs.info.ecuapass_feedback import EcuFeedback
from ecuapassdocs.info.ecuapass_utils import Utils

from .ecuapass_azure import EcuAzure
from .bot_codebin import  CodebinBot
from .ecuapass_exceptions import EcudocDocumentNotFoundException, EcudocConnectionNotOpenException

USAGE="\n\
Extract info from ECUAPASS documents in PDF (cartaporte|manifiesto|declaracion).\n\
USAGE: ecuapass_doc.py <PDF document>\n"

def main ():
	if (len (sys.argv) < 2):
		print (USAGE)
	else:
		docFilepath = sys.argv [1]
		CodebinBot.initCodebinWebdriver ()
		ecuDoc = EcuDoc ()
		ecuDoc.extractDocumentFields (docFilepath, os.getcwd())

def printx (*args, flush=True, end="\n"):
	message = " ".join (args)
	print ("SERVER:", *args, flush=flush, end=end)
	return message

#-----------------------------------------------------------
# Run cloud analysis
#-----------------------------------------------------------
class EcuDoc:
	#----------------------------------------------------------------
	#-- Analyze one document given its path
	# Extract fields info from PDF document (using CODEBIN bot)
	#----------------------------------------------------------------
	def analyzeDocument (docFilepath, runningDir, webdriver):
		try:
			workingDir = os.path.dirname (docFilepath)

			# Check if PDF is a valid ECUAPASS document
			if not EcuDoc.isValidDocument (docFilepath):
				return f"Tipo de documento '{docFilepath}' no válido"

			# Create and start threads for processing files
			os.chdir (workingDir)

			# Load "empresa": reads and checks if "settings.txt" file exists
			settings = Utils.loadSettings (runningDir)
			empresa  = settings ["empresa"]

			# Start document processing
			filename       = os.path.basename (docFilepath)
			docType        = Utils.getDocumentTypeFromFilename (filename)
			outputFile     = EcuDoc.extractFields (docFilepath, docType, settings, webdriver)
			fieldsJsonFile = EcuDoc.convertNewlinesToWin (outputFile)

			# Send file as feedback
			#EcuFeedback.sendFile (empresa, fieldsJsonFile)
			#EcuFeedback.sendFile (empresa, docFilepath)

			# e.g. CartaporteByza, ManifiestoNTA, ...
			DOCCLASS = EcuDoc.getInfoDocumentClass (empresa, docType, fieldsJsonFile, runningDir)

			# Get document Ecuapass and document fields
			ecuFile   = EcuDoc.saveFields (DOCCLASS.getMainFields (),   filename, "ECUFIELDS")
			docFile   = EcuDoc.saveFields (DOCCLASS.getDocFields (),   filename, "DOCFIELDS")
			cbinFile  = EcuDoc.saveFields (DOCCLASS.getCodebinFields(),  filename, "CBINFIELDS")
			edocsFile = EcuDoc.saveFields (DOCCLASS.getEcuapassdocsFields(), filename, "EDOCSFIELDS")

			# Full path as Java search the doc
			return (printx (f"EXITO: Documento procesado: '{docFilepath}'"))
		except EcudocDocumentNotFoundException as ex:
			return (printx (f"ERROR: Documento no encontrado:\\\\{str(ex)}"))
		except EcudocConnectionNotOpenException as ex:
			return (printx (f"ERROR: Problamas conectAndose al CODEBIN: {str(ex)}"))
		except Exception as ex:
			Utils.printException (ex)
			return (printx (f"ERROR: No se pudo extraer campos del documento:\\\\{str(ex)}"))

	#------------------------------------------------------
	#-- Get document fields from PDF document
	#------------------------------------------------------
	def extractFields (docFilepath, docType, settings, webdriver):
		# CACHE: Check codebin .json cache document
		fieldsJsonFile = EcuDoc.loadCodebinCache (docFilepath)
		if fieldsJsonFile:
			return fieldsJsonFile

		# CODEBIN BOT: Get data from CODEBIN web
		printx (">>>>>>>>>>>>>>>>>>>>>> Getting document fields <<<<<<<<<<<<<<<<<<<<<<<")
		filename = os.path.basename (docFilepath)
		printx (f"+++ Buscando documento '{filename}' en CODEBIN...")
		codebinBot = CodebinBot (docFilepath, settings, webdriver)
		fieldsJsonFile = codebinBot.getDocumentFile ()
		Utils.printx (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

		if fieldsJsonFile:
			return fieldsJsonFile

		raise Exception ("No se pudo procesar documento")

#		# CACHE: Check azure .pkl cache document
#		fieldsJsonFile = EcuDoc.loadAzureCache (docFilepath)
#		if fieldsJsonFile:
#			return fieldsJsonFile
#
#		# EMBEDDED: Check embedded fields
#		fieldsJsonFile = EcuDoc.getEmbeddedFieldsFromPDF (docFilepath)
#		if fieldsJsonFile:
#			return fieldsJsonFile


		# Azure CLOUD: Analyzing the document using the cloud
		#fieldsJsonFile = EcuAzure.analyzeDocument (docFilepath, docType, empresa)
		#if fieldsJsonFile:
		#	return fieldsJsonFile

	#----------------------------------------------------------------
	# Change Windows newlines (\r\n( to linux newlines (\n)
	#----------------------------------------------------------------
	def convertNewlinesToWin (jsonFilename):
		fields = json.load (open (jsonFilename))
		for key in fields.keys ():
			content = fields [key]["content"]
			if content:
				fields [key]["content"] = content.replace ("\r\n", "\n")

		json.dump (fields, open (jsonFilename, "w"), indent=4)
		return jsonFilename
			
		
	#----------------------------------------------------------------
	#-- Load previous result
	#----------------------------------------------------------------
	def loadCodebinCache (docFilepath):
		fieldsJsonFile = None
		try:
			#filename       = os.path.basename (docFilepath)
			filename       = docFilepath
			cacheFilename = f"{filename.split ('.')[0]}-CBINFIELDS.json"
			printx (f"Buscando archivo CODEBIN cache '{cacheFilename}'...")
			if os.path.exists (cacheFilename): 
				printx ("...Archivo encontrado.")
				with open (cacheFilename, 'r') as inFile:
					codebinValues = json.load (inFile)
				docType        = Utils.getDocumentTypeFromFilename (docFilepath)
				docNumber      = Utils.getDocumentNumberFromFilename (docFilepath)
				azureValues    = Utils.getAzureValuesFromCodebinValues (docType, codebinValues, docNumber)
				fieldsJsonFile = Utils.saveFields (azureValues, docFilepath, "DOCFIELDS")
		except:
			Utils.printException (f"Cargando documento desde cache: '{filename}'")
			raise

		return (fieldsJsonFile)

	def loadAzureCache (docFilepath):
		fieldsJsonFile = None
		try:
			#filename       = os.path.basename (docFilepath)
			filename       = docFilepath
			pickleFilename = f"{filename.split ('.')[0]}-CACHE.pkl"
			printx (f"Buscando archivo cache '{pickleFilename}'...")
			if os.path.exists (pickleFilename): 
				printx ("...Archivo encontrado.")
				with open (pickleFilename, 'rb') as inFile:
					result = pickle_load (inFile)
				fieldsJsonFile = EcuAzure.saveResults (result, filename)
			else:
				printx (f"...Archivo cache no existe'")
		except:
			printx (f"EXCEPCION: cargando documento desde cache: '{filename}'")
			Utils.printException ()
			#raise

		return (fieldsJsonFile)
	
	#----------------------------------------------------------------
	#-- Get embedded fields info from PDF
	#----------------------------------------------------------------
	def getEmbeddedFieldsFromPDF (pdfPath):
		fieldsJsonPath = pdfPath.replace (".pdf", "-FIELDS.json")
		try:
			with open(pdfPath, 'rb') as pdf_file:
				pdf_reader = PyPDF2.PdfReader(pdf_file)

				# Assuming the hidden form field is added to the first page
				first_page = pdf_reader.pages[0]

				# Extract the hidden form field value 
				text     = first_page.extract_text()  
				jsonText = re.search ("Embedded_jsonData: ({.*})", text).group(1)
				printx ("Obteniendo campos desde el archivo PDF...")
				fieldsJsonDic  = json.loads (jsonText)
				json.dump (fieldsJsonDic, open (fieldsJsonPath, "w"), indent=4, sort_keys=True)
		except Exception as e:
			Utils.printx ("EXCEPCION: Leyendo campos embebidos en el documento PDF.")
			return None

		return (fieldsJsonPath)


	#-- Save fields dict in JSON 
	def saveFields (fieldsDict, filename, suffixName, sort=False):
		prefixName	= filename.split(".")[0]
		outFilename = f"{prefixName}-{suffixName}.json"
		fp = open (outFilename, "w") 
		json.dump (fieldsDict, fp, indent=4)
		fp.close ()
		#with open (outFilename, "w") as fp:
		#	json.dump (fieldsDict, fp, indent=4, default=str, sort_keys=False)

		return outFilename

	#-----------------------------------------------------------
	# Return document class for document type and empresa
	#-----------------------------------------------------------
	def getInfoDocumentClass (empresa, docType, fieldsJsonFile, runningDir):
		DOCCLASS = None
		if docType.upper() == "CARTAPORTE":
			if "BYZA" in empresa:
				DOCCLASS  = CartaporteByza (fieldsJsonFile, runningDir)
			elif "BOTERO" in empresa:
				DOCCLASS  = CartaporteBotero (fieldsJsonFile, runningDir)
			elif "NTA" in empresa:
				DOCCLASS  = CartaporteNTA (fieldsJsonFile, runningDir)
			elif "SYTSA" in empresa:
				DOCCLASS  = CartaporteSytsa (fieldsJsonFile, runningDir)
		elif docType.upper() == "MANIFIESTO":
			if "BYZA" in empresa:
				DOCCLASS = ManifiestoByza (fieldsJsonFile, runningDir)
			elif "BOTERO" in empresa:
				DOCCLASS = ManifiestoBotero (fieldsJsonFile, runningDir)
			elif "NTA" in empresa:
				DOCCLASS = ManifiestoNTA (fieldsJsonFile, runningDir)
			elif "SYTSA" in empresa:
				DOCCLASS = ManifiestoSytsa (fieldsJsonFile, runningDir)
		elif docType.upper() == "DECLARACION":
			Utils.printx (f"ALERTA: '{docType}' no están soportadas")
			raise Exception (f"Tipo de documento '{docType}' desconocido")

		return DOCCLASS

	#----------------------------------------------------------------
	#-- Check if document filename is an image (.png) or a PDF file (.pdf)
	#----------------------------------------------------------------
	def isValidDocument (filename):
		extension = filename.split (".")[1]
		if extension.lower() in ["PDF", "pdf"]:
			return True
		return False

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()
