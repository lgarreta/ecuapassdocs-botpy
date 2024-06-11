
import os, time, sys
import pyautogui as py
from traceback import format_exc as traceback_format_exc

from ecuapassdocs.info.ecuapass_utils import Utils

from .ecuapass_bot import EcuBot

#----------------------------------------------------------
# Globals
#----------------------------------------------------------
sys.stdout.reconfigure(encoding='utf-8')
PAUSE = 0

def main ():
	args = sys.argv 
	jsonFilepath = args [1]
	runningDir   = os.getcwd()
	mainBotCartaporte (jsonFilepath, runningDir)

#----------------------------------------------------------
# Main function for testing
#----------------------------------------------------------
def mainBotCartaporte (jsonFilepath, runningDir):
	bot = EcuBotCartaporte (jsonFilepath, runningDir)
	bot.start ()
	
#--------------------------------------------------------------------
# self for filling Ecuapass cartaporte web form (in flash)
#--------------------------------------------------------------------
class EcuBotCartaporte (EcuBot):
	def __init__(self, jsonFilepath, runningDir):
		super().__init__ (jsonFilepath, runningDir, "CARTAPORTE")

	#-- Main function for testing
	def fillEcuapass (self):
			self.skipN (2)
			# Encabezado
			self.fillBoxIter  (self.fields ["01_Distrito"])
			self.fillText ("02_NumeroCPIC")
			self.fillText ("03_MRN")
			self.fillText ("04_MSN")
			self.fillBoxCheck ("05_TipoProcedimiento")
			#self.fillBoxCheck ("06_EmpresaTransporte") # Selected by default
			py.press ("Tab")
			self.fillBoxCheck ("07_DepositoMercancia", "TAB_NOCHECK")

			self.fillText ("08_DirTransportista")
			self.fillText ("09_NroIdentificacion")

			self.scrollN (5)

			# Remitente
			self.fillSubject ("REMITENTE", "05_TipoProcedimiento", "10_PaisRemitente", 
							  "11_TipoIdRemitente", "12_NroIdRemitente", "14_NombreRemitente",
							  "15_DireccionRemitente", "13_NroCertSanitario")
			# Destinatario
			self.fillSubject ("DESTINATARIO", "05_TipoProcedimiento", "16_PaisDestinatario",
							  "17_TipoIdDestinatario", "18_NroIdDestinatario", 
							  "19_NombreDestinatario", "20_DireccionDestinatario")
			# Consignatario
			self.fillSubject ("CONSIGNATARIO", "05_TipoProcedimiento", "21_PaisConsignatario", 
							  "22_TipoIdConsignatario", "23_NroIdConsignatario", 
							  "24_NombreConsignatario", "25_DireccionConsignatario")

			self.scrollN (10)

			# Notificado
			self.fillText ("26_NombreNotificado")
			self.fillText ("27_DireccionNotificado")
			self.fillBoxCheck ("28_PaisNotificado")

			# Paises y fechas: Recepcion, Embarque, Entrega
			self.scrollN (5)
			self.fillBoxCheck ("29_PaisRecepcion"); self.skipN (2)
			self.fillBoxCheck ("32_PaisEmbarque"); self.skipN (2)
			self.fillBoxCheck ("35_PaisEntrega"); 
			self.skipN (12)
			self.fillBoxCheck ("48_PaisMercancia"); # Pais INCOTERM
			self.skipN (13)
			self.fillBoxCheck ("62_PaisEmision"); 

			# Go back to fill other fields
			self.skipN (33, "LEFT"); py.sleep (0.01)
			self.fillBoxCheck ("30_CiudadRecepcion"); 
			self.fillDate     ("31_FechaRecepcion"); self.skipN (2)
			self.fillBoxCheck ("33_CiudadEmbarque"); 
			self.fillDate     ("34_FechaEmbarque"); self.skipN (2)
			self.fillBoxCheck ("36_CiudadEntrega"); 
			self.fillDate     ("37_FechaEntrega"); py.press ("Tab")
			# Condiciones
			self.fillBoxCheck ("38_CondicionesTransporte")
			self.fillBoxCheck ("39_CondicionesPago")
			# Mercancia
			self.fillText     ("40_PesoNeto")
			self.fillText     ("41_PesoBruto")
			self.fillText     ("42_TotalBultos")
			self.fillText     ("43_Volumen")
			self.fillText     ("44_OtraUnidad")
			self.fillText     ("45_PrecioMercancias")
			# INCOTERM
			self.scrollN (5)
			self.fillBoxCheck ("46_INCOTERM")
			self.fillBoxCheck ("47_TipoMoneda"); py.press ("Tab")
			# Ciudad INCOTERM
			self.fillBoxCheck ("49_CiudadMercancia")
			# Gastos
			self.fillText     ("50_GastosRemitente")
			self.fillBoxCheck ("51_MonedaRemitente")
			self.fillText     ("52_GastosDestinatario")
			self.fillBoxCheck ("53_MonedaDestinatario")
			self.fillText     ("54_OtrosGastosRemitente")
			self.fillBoxCheck ("55_OtrosMonedaRemitente")
			self.fillText     ("56_OtrosGastosDestinatario")
			self.fillBoxCheck ("57_OtrosMonedaDestinataio")
			self.fillText     ("58_TotalRemitente")
			self.fillText     ("59_TotalDestinatario")
			# Documentos
			self.fillText     ("60_DocsRemitente")
			# Emision
			self.fillDate     ("61_FechaEmision"); py.press ("Tab"); py.press ("Tab")
			self.fillBoxCheck ("63_CiudadEmision")

			# Instrucciones
			self.scrollN (17)
			self.fillText ("64_Instrucciones")
			self.fillText ("65_Observaciones")

			self.skipN (3)

			# Detalles
			self.fillText     ("66_Secuencia")
			self.fillText     ("67_TotalBultos")
			self.fillBoxCheck ("68_Embalaje")
			self.fillText     ("69_Marcas")
			self.fillText     ("70_PesoNeto")
			self.fillText     ("71_PesoBruto")
			self.fillText     ("72_Volumen")
			self.fillText     ("73_OtraUnidad")

			# IMOs
			self.fillText     ("74_Subpartida"); py.press ("Tab")
			self.fillBoxCheck ("75_IMO1")
			self.fillBoxCheck ("76_IMO2")
			self.fillBoxCheck ("77_IMO2")
			self.fillText     ("78_NroCertSanitario")
			self.fillText     ("79_DescripcionCarga")

			# Valid RUC ID with find button in 'Remitente', 'Destinatario', 'Consignatario'
			#if "IMPORTACION" in self.fields ["05_TipoProcedimiento"]:
				
			return (f"Ingresado exitosamente el documento {self.jsonFilepath}")
			

if __name__ == "__main__":
	main()


