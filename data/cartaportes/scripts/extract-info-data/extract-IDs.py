#!/usr/bin/env python3
import re, sys
from traceback import format_exc as traceback_format_exc

def main ():
	#text = "FABRICATO S.A.\nKR 50 38-320\nBELLO COLOMBIA RUC - 890900908-4"
	text = "FABRICATO S.A.\nKR 50 38-320\nRUC - 890900908-4  PAZ DE ARIPORO-COLOMBIA"

	subject = getSubjectInfo (text)
	print (subject)

def getSubjectInfo (text):
	subject = {"nombre":None, "direccion":None, "pais":None, "ciudad":None, "tipoId":None, "numeroId":None}

	text, subject = getIdInfo (text, subject)
	text, subject = getCiudadPaisInfo (text, subject)

	textLines = text.split ("\n")
	subject ["nombre"] = textLines [0].strip()
	if len (textLines) == 2:
		subject ["direccion"] = textLines [1].strip()
	elif len (textLines) > 2:
		message = "EXCEPCION: Información sujeto con muchas líneas"
		raise Exception (message)
	return (subject)

#-- Get ciudad + pais using data from ecuapass
def getCiudadPaisInfo (text, subject):
	try:
		rePais = ".*?(ECUADOR|COLOMBIA|PERU|BOLIVIA)$"
		pais   = re.search (rePais, text).group (1)
		subject ["pais"] = pais
		cities = getCitiesString (pais)

		reLocation = f"(?P<ciudad>{cities}).*(?P<pais>{pais})\s*"
		result = re.search (reLocation, text, flags=re.I)
		subject ["ciudad"] = result.group ("ciudad") if result else None
		text	= text.replace (result.group (0), "")
	except:
		print ("EXCEPCION: Obteniendo ciudad-pais")
		print (traceback_format_exc())

	return (text.strip(), subject)

#-- Get and extract id type and number ----------------------------
def getIdInfo (text, subject):
	try:
		reId	= r"(?P<tipo>(RUC|NIT)).*?(?P<id>\d+)\-?\d+\s*"
		result	= re.search (reId, text, flags=re.S)
		text	= re.sub (reId, "", text, flags=re.S)
	 
		subject ["tipoId"] = result.group ("tipo") if result else None
		subject ["numeroId"] = result.group ("id") if result else None
	except:
		print ("EXCEPCION: Obteniendo información ID")
		print (traceback_format_exc())

	return (text, subject)

#-- Load cities from DB and create a piped string of cites ----------
def getCitiesString (pais):
	if (pais=="COLOMBIA"):
		filename = os.path.join ("data", "ciudades_colombia.txt")
	elif (pais=="ECUADOR"):
		filename = os.path.join ("data", "ciudades_ecuador.txt"

	# Load cities
	with open (filename, encoding="latin-1") as fp:
		citiesAll = fp.readlines ()

	reCity = "\[.+\]\s(.+)"
	cities = []
	for line in citiesAll:
		city = re.search (reCity, line).group(1)
		cities.append (city.lower())

	citiesString = "|".join (cities)
	return citiesString

main()
