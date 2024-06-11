
import os, sys 
import pyautogui as py
from traceback import format_exc as traceback_format_exc

from ecuapassdocs.info.ecuapass_utils import Utils

from .ecuapass_bot import EcuBot

#----------------------------------------------------------
# Globals
#----------------------------------------------------------
win   = None	 # Global Ecuapass window  object
GLOBAL_PAUSE = 0.03
SLOW_PAUSE   = 0.05

def main ():
	args = sys.argv 
	jsonFilepath = args [1]
	runningDir   = os.getcwd()
	mainBotDeclaracion (jsonFilepath, runningDir)

#----------------------------------------------------------
# Main function for testing
#----------------------------------------------------------
def mainBotDeclaracion (jsonFilepath, runningDir):
	Utils.printx (f"Versión0.96. Iniciando digitación de documento '{jsonFilepath}'")
	Utils.printx (f"Directorio actual: ", os.getcwd())
	Utils.runningDir = runningDir
	result = EcuBotDeclaracion.fillEcuapass (jsonFilepath)
	return result

#--------------------------------------------------------------------
# EcuBot for filling Ecuapass cartaporte web form (in flash)
#--------------------------------------------------------------------
class EcuBotDeclaracion:
	def fillEcuapass (jsonFilepath):
		try:
			py.PAUSE = GLOBAL_PAUSE

			global win
			fieldsConfidence = Utils.readJsonFile (jsonFilepath)
			fields = Utils.removeConfidenceString (fieldsConfidence)
			
			win    = Utils.activateEcuapassWindow ()
			Utils.scrollWindowToBeginning ()
			Utils.detectEcuapassDocumentWindow ("declaracion")
			Utils.clearWebpageContent ()
			py.press ("Tab"); py.press ("Tab")

			print ("\n>>>>>> Declaración de Tránsito Aduanero Internacional <<<")
			EcuBot.fillBoxSimpleIteration  (fields, "01_Distrito"); py.press ("Tab")
			EcuBot.fillDate     (fields, "02_Fecha_Emision"); py.press ("Tab")
			EcuBot.fillBox      (fields, "03_Procedimiento"); py.press ("Tab")
			EcuBot.fillText     (fields, "04_Numero_DTAI"); py.press ("Tab")
			EcuBot.fillBox      (fields, "05_Pais_Origen"); py.press ("Tab");

			# Aduana de carga
			EcuBot.fillBox      (fields, "06_Pais_Carga"); py.press ("Tab");
			EcuBot.fillBox      (fields, "07_Aduana_Carga"); py.press ("Tab");

			# Aduana de partida
			EcuBot.fillBox      (fields, "08_Pais_Partida"); py.press ("Tab");
			EcuBot.fillBox      (fields, "09_Aduana_Partida"); py.press ("Tab");

			# Aduana de destino
			EcuBot.fillBox      (fields, "10_Pais_Destino"); py.press ("Tab");
			EcuBot.fillBox      (fields, "11_Aduana_Destino"); py.press ("Tab");

			py.press ("Tab")

		except Exception as ex:
			Utils.printx (f"EXCEPCION: Digitando documento '{jsonFilepath}'")
			Utils.printx (traceback_format_exc())
			return (str(ex))

		return (f"Ingresado exitosamente el documento {jsonFilepath}")

#--------------------------------------------------------------------
# Call to main
#--------------------------------------------------------------------
if __name__ == "__main__":
	main()

