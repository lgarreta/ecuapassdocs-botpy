
import os, json, time

# For doc
from pickle import dump as pickle_dump

# For Azure
import azure.core.credentials 
from azure.ai.formrecognizer import DocumentAnalysisClient

from ecuapassdocs.info.ecuapass_data import EcuData
from ecuapassdocs.info.ecuapass_utils import Utils

#-----------------------------------------------------------
# Custom document built with the Azure Form Recognizer 
#-----------------------------------------------------------
class EcuAzure:
	AzureKeyCredential = azure.core.credentials.AzureKeyCredential

	#-----------------------------------------------------------------
	#-- Online processing. Return the first document, save resuts
	#-----------------------------------------------------------------
	def analyzeDocument (docFilepath, documentType, empresa):
		docJsonFile = None
		try:
			credentialsDict  = EcuAzure.initCredentials (documentType, empresa)
			lgEndpoint		 = credentialsDict ["endpoint"]
			lgKey			 = credentialsDict ["key"]	
			lgLocale		 = credentialsDict ["locale"]
			lgModel			 = credentialsDict ["modelId"]

			lgCredential = EcuAzure.AzureKeyCredential (lgKey)
			docClient	 = DocumentAnalysisClient (endpoint = lgEndpoint, 
												   credential = lgCredential)
			# Read the file into memory
			with open(docFilepath, "rb") as fp:
				poller = docClient.begin_analyze_document (lgModel, document=fp, locale=lgLocale)

			print ("\t>>>", "Polling result....")
			result	  = poller.result()
			document  = result.documents [0]
			docDict   = document.to_dict ()
			fields    = docDict ["fields"]
		

			# Save original result as pickled and json files
			print ("\t>>>", "Saving result....")
			docFilename = os.path.basename (docFilepath)
			fieldsJsonFile = EcuAzure.saveResults (result, docFilename)
		except Exception as ex:
			printx (ex.args [0])
			printx (f"ALERTA: Problemas analizando documento: '{docFilepath}'" )
			raise
			
		return (fieldsJsonFile)

	#-----------------------------------------------------------
	# Call the model according to prefix filename:"CARTAPORTE|MANIFIESTO|DECLARACION"
	#-----------------------------------------------------------
	def initCredentials (documentType, empresa):
		keys = { "key1": "30366959fe1649be9d98fde7cd4a938b",
			     "endpoint": "https://eastus.api.cognitive.microsoft.com/"}
		#old_keys = { "key1": "f18ce9601aaa4196926d846957d7f70a",
		#	          "endpoint": "https://lgtestfr.cognitiveservices.azure.com/" }

		try:
			print ("\t>>> Leyendo credenciales...")
			credentialsDict = {}
			credentialsDict ["endpoint"] = keys ["endpoint"]
			credentialsDict ["key"]		 = keys ["key1"]
			credentialsDict ["locale"]	 = "es-CO"

			empresaData = EcuData.getEmpresaInfo (empresa)
			print ("\t>>> Empresa actual: ", empresaData ["nombre"])
			if (documentType in "CARTAPORTE"):
				#credentialsDict ["modelId"]  = empresaData ["modelCartaportes"]
				credentialsDict ["modelId"]  = "model-cartaporte-codebin"
			elif (documentType in "MANIFIESTO"):
				print ("\t>>> Modelo actual: ", empresaData ["modelManifiestos"])
				credentialsDict ["modelId"]  = empresaData ["modelManifiestos"]
			elif (documentType in "DECLARACION"):
				credentialsDict ["modelId"]  = empresaData ["modelDeclaraciones"]
			else:
				raise Exception (f"ALERTA:Tipo de documento '{documentType}' desconocido")
		except Exception as ex:
			printx ("ERROR: Problemas inicializando credenciales.")
			raise

		print ("-- Credenciales:")
		print (credentialsDict)
		return (credentialsDict)

	#-- Save request result as pickle and json files
	#-- Return output filename for json fields 
	def saveResults (result, docFilepath):
		rootName = docFilepath.split ('.')[0]

		# Save results as Pickle 
		outPickleFile = f"{rootName}-CACHE.pkl"
		with open(outPickleFile, 'wb') as outFile:
			pickle_dump (result, outFile)

		# Add newlines
		resultDict           = result.to_dict ()
		documentDictNewlines = EcuAzure.getDocumentWithNewlines (resultDict)

		# Get fields and write down
		fields	             = documentDictNewlines ["fields"]
		fieldsJsonFile       = f"{rootName}-FIELDS" ".json"
		with open (fieldsJsonFile, 'w') as outFile:
			json.dump (fields, outFile, indent=4, default=str, sort_keys=True)

		return (fieldsJsonFile)
#		# Save results as JSON file
#		outJsonFile = f"{rootName}-CACHE.json"
#		with open (outJsonFile, 'w') as outFile:
#			json.dump (resultDict, outFile, indent=4, default=str, sort_keys=True)
#
#		# Save result document as JSON file
#		document	 = result.documents [0]
#		documentDict = document.to_dict ()
#		outJsonFile = f"{rootName}-NONEWLINES" ".json"
#		with open (outJsonFile, 'w') as outFile:
#			json.dump (documentDict, outFile, indent=4, default=str, sort_keys=True)
#
#		# Save document with original (newlines) content
#		docJsonNewlinesFile  = f"{rootName}-DOCUMENT" ".json"
#		with open (docJsonNewlinesFile, 'w') as outFile:
#			json.dump (documentDictNewlines, outFile, indent=4, default=str, sort_keys=True)
#
		# Save fields document as JSON file
#		#dicPais  =  {"00_Pais": EcuAzure.getWorkingCountry()}
#		#fiedlds  = fields.update (dicPais)

	def getCloudName ():
		return "azure"


	#-- Add newlines to document content 
	def getDocumentWithNewlines (resultsDict):
		#-- Determine whether two floating-point numbers are close in value.
		def isClose(a, b, rel_tol=1e-09, abs_tol=0.0):
			if abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol):
				return True
			return False

		def areClose(float1, float2, tolerance=1e-1):
			return abs(float1 - float2) < tolerance	

		#-- Check if the line is whithin the field box dimensions --
		def isContained (line, field):
			lineContent = line ["content"]
			xl = line ["polygon"][0]["x"]
			yl = line ["polygon"][0]["y"]
			#print ("\t\t> Coords line:", xl, yl)

			fieldContent = field ["content"]
			if (fieldContent == None):
				return False

			xf1   = field ["bounding_regions"][0]["polygon"][0]["x"]
			yf1   = field ["bounding_regions"][0]["polygon"][0]["y"]
			yf2   = field ["bounding_regions"][0]["polygon"][2]["y"]
			#print ("\t\t> Coords field", xf1, yf1, yf2)

			if (lineContent in fieldContent and areClose (xl, xf1) and 
				(areClose (yl, yf1) or yl >= yf1 and yl <= yf2)):
				return True

			return False
		#--------------------------------------------------------------

		lines  = resultsDict ["pages"][0]["lines"]
		fields = resultsDict ["documents"][0]["fields"]
		#fields = {"29_Mercancia_Descripcion": resultsDict ["documents"][0]["fields"]["29_Mercancia_Descripcion"]}

		for line in lines:
			lineContent = line ["content"]
			#print (">>> lineContent:", lineContent)
			#print (">", lineContent)
			for key in fields:
				field = fields [key]
				fieldContent = field ["content"]
				#print ("\t>", fieldContent)

				if isContained (line, field):
					#print (">>> CONTAINED")
					newlineContent = fieldContent.replace (lineContent+" ", lineContent+"\n")
					fields [key] ["content"] = newlineContent
					break

			resultsDict ["documents"][0]["fields"] = fields

		return (resultsDict ["documents"][0])

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()
