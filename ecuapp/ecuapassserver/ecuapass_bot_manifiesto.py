
import os, sys 
import pyautogui as py
from traceback import format_exc as traceback_format_exc

from ecuapassdocs.info.ecuapass_utils import Utils

from .ecuapass_bot import EcuBot

#----------------------------------------------------------
# Globals
#----------------------------------------------------------
sys.stdout.reconfigure(encoding='utf-8')

def main ():
	args = sys.argv 
	jsonFilepath = args [1]
	runningDir   = os.getcwd()
	mainBotManifiesto (jsonFilepath, runningDir)

#----------------------------------------------------------
# Main function for testing
#----------------------------------------------------------
def mainBotManifiesto (jsonFilepath, runningDir):
	bot = EcuBotManifiesto (jsonFilepath, runningDir)
	message = bot.start ()
	return message
	
#--------------------------------------------------------------------
# self for filling Ecuapass cartaporte web form (in flash)
#--------------------------------------------------------------------
class EcuBotManifiesto (EcuBot):
	def __init__(self, jsonFilepath, runningDir):
		super().__init__ (jsonFilepath, runningDir, "MANIFIESTO")

	def fillEcuapass (self):
		self.skipN (2)

		# print ("\n>>>>>> Identificacion del Transportista Autorizado <<<")
		
		py.PAUSE = self.SLOW_PAUSE
		self.fillBoxCheck      ("01_Tipo_Procedimiento")
		self.fillBoxCheck      ("02_Sector")
		py.PAUSE = self.NORMAL_PAUSE
		self.fillDate     ("03_Fecha_Emision"); py.press ("Tab")
		self.fillBoxIter  (self.fields ["04_Distrito"])
		self.fillText     ("05_MCI")
		self.selFirstItemFromBox (); py.press ("Tab"); 

		# print (">>> Identificación Permisos")
		[py.press ("left") for i in range (3)]

		self.fillRButton  ("07_TipoPermiso_CI")
		self.fillRButton  ("08_TipoPermiso_PEOTP")
		self.fillRButton  ("09_TipoPermiso_PO")

		# print ("\n>>>>>> Identificacion del Transportista Autorizado <<<")
		self.fillText     ("10_PermisoOriginario")
		self.fillText     ("11_PermisoServicios1")
		self.fillText     ("12_PermisoServicios2")
		self.fillText     ("13_PermisoServicios3")
		self.fillText     ("14_PermisoServicios4")
		#self.fillText     ("15_NombreTransportista"); py.press ("Tab"); # Autoselected
		#self.fillText     ("16_DirTransportista"); py.press ("Tab");    # Autoselected

		self.skipN (2)

		self.scrollN (10)

		# print ("\n>>>>>> Identificacion del Vehículo Habilitado <<<")
		self.fillText     ("17_Marca_Vehiculo")
		self.fillText     ("18_Ano_Fabricacion")
		self.fillBoxCheck      ("19_Pais_Vehiculo")
		self.fillText     ("20_Placa_Vehiculo")
		self.fillText     ("21_Nro_Chasis")
		self.fillText     ("22_Nro_Certificado")
		self.fillBoxCheck      ("23_Tipo_Vehiculo")

		# CHECK for errors
		self.checkErrorDialogBox ("image-box-FormatoPermiso")

		# print ("\n>>>>>> Identificacion de la Unidad de Carga (Remolque) <<<")
		self.fillText     ("24_Marca_remolque")
		self.fillText     ("25_Ano_Fabricacion")
		self.fillText     ("26_Placa_remolque")
		self.fillBoxCheck      ("27_Pais_remolque")
		self.fillText     ("28_Nro_Certificado")
		self.fillText     ("29_Otra_Unidad")

		# print ("\n>>>>>> Identificacion de la Tripulacion <<<")
		self.fillBoxCheck      ("30_Pais_Conductor")
		self.fillBoxCheck      ("31_TipoId_Conductor")
		self.fillText     ("32_Id_Conductor")
		self.fillBoxCheck      ("33_Sexo_Conductor")
		self.fillDate     ("34_Fecha_Conductor"); py.press ("TAB")
		self.fillText     ("35_Nombre_Conductor")
		self.fillText     ("36_Licencia_Conductor")
		self.fillText     ("37_Libreta_Conductor")

		self.fillBoxCheck      ("38_Pais_Auxiliar")
		self.fillBoxCheck      ("39_TipoId_Auxiliar")
		self.fillText     ("40_Id_Auxiliar")
		self.fillBoxCheck      ("41_Sexo_Auxiliar")
		self.fillDate     ("42_Fecha_Auxiliar"); py.press ("Tab")
		self.fillText     ("43_Nombre_Auxiliar")
		self.fillText     ("44_Apellido_Auxiliar")
		self.fillText     ("45_Licencia_Auxiliar")
		self.fillText     ("46_Libreta_Auxiliar")

		self.scrollN (15)

		#--------------------------------------------------
		# Datos Sobre la Carga
		#--------------------------------------------------
		#-- Fist fill paises
		self.fillBoxCheck      ("47_Pais_Carga"); py.press ("Tab")
		self.fillBoxCheck      ("49_Pais_Descarga"); 
		self.skipN (6)
		self.fillBoxCheck      ("56_Pais"); py.press ("Tab")
		self.fillBoxCheck      ("58_AduanaDest_Pais"); py.press ("Tab")
		self.skipN (7)
		self.fillBoxCheck      ("64_AduanaCruce_Pais"); 

		#-- Go back to fill the other fields
		self.skipN (20, "LEFT")
		self.fillBoxCheck      ("48_Ciudad_Carga"); py.press ("Tab")
		self.fillBoxCheck      ("50_Ciudad_Descarga")
		self.fillBoxCheck      ("51_Tipo_Carga")
		self.fillText          ("52_Descripcion_Carga"); 
		self.fillText          ("53_Precio_Mercancias")
		self.fillBoxCheck      ("54_Incoterm")
		self.fillBoxCheck      ("55_Moneda"); py.press ("Tab")
		self.fillBoxCheck      ("57_Ciudad"); py.press ("Tab")
		self.fillBoxCheck      ("59_AduanaDest_Ciudad")
		self.fillText          ("60_Peso_NetoTotal")
		self.fillText          ("61_Peso_BrutoTotal")
		self.fillText          ("62_Volumen")
		self.fillText          ("63_OtraUnidad")
		# Jump to 65_AduanaCruce_Ciudad
		self.skipN (4)
		self.fillBoxCheck      ("65_AduanaCruce_Ciudad")

		#--------------------------------------------------
		# Aduana(s) de Cruce de Fronteras
		#--------------------------------------------------
		# --Aduana cruce
		py.press ("space"); py.sleep (0.1); py.press ("space");
		self.skipN (2, "LEFT")
		# --Aduana destino
		self.fillBoxCheck      ("58_AduanaDest_Pais")
		py.sleep (0.2)
		self.fillBoxCheck      ("59_AduanaDest_Ciudad")
		py.press ("space"); py.sleep (0.1); py.press ("space");

		#--------------------------------------------------
		# Datos de Detalle de la Carga
		#--------------------------------------------------
		self.skipN (6)
		self.scrollN (20)

		self.fillText     ("66_Secuencia")
		self.skipN (4)    # Skiap Fixed values and Cartaporte
		self.fillText     ("70_TotalBultos")
		self.fillBox      ("71_Embalaje")
		self.fillText     ("72_Marcas")
		self.fillText     ("73_Peso_Neto")
		self.fillText     ("74_Peso_Bruto")
		self.fillText     ("75_Volumen")
		self.fillText     ("76_OtraUnidad")
		self.fillText     ("77_Nro_UnidadCarga")
		self.fillBoxCheck ("78_Tipo_UnidadCarga")
		self.fillBoxCheck ("79_Cond_UnidadCarga")
		self.fillText     ("80_Tara")
		self.fillText     ("81_Descripcion")

		self.scrollN (10)

		self.skipN (4)
		self.fillText     ("82_Precinto")

		print ("\n>>>>>> Buscando/Seleccionando cartaporte <<<<<<")

		self.skipN (18, "LEFT")          # Go back to Find Button  
		py.press ("space"); py.sleep (2) # Press Find button
		
		self.skipN (3);                  # Go to "fecha/hora" and select "Mes" 
		self.fillBoxIter ("Mes", "NO_TAB")
		self.skipN (3); py.press ("end") # Go to "tipo documento" and select "CPIC"
		self.skipN (3); py.press ("space"); py.sleep (3) # "Consultar CPICs"
		self.skipN (2, "LEFT"); self.fillText     ("69_CPIC", "NO_TAB"); # Fill "Cartaporte" number
		self.skipN (4)                   # Go to found cartaportes
		py.press ("down")
		py.press ("enter")
		self.clickSelectedCartaporte ("69_CPIC")
		py.press ("Tab"); py.press ("space")

		Utils.printx (f"MENSAJE: Finalizada digitación. Seleccione la Carta de Porte. ")

#--------------------------------------------------------------------
# Call to main
#--------------------------------------------------------------------
if __name__ == "__main__":
	main()

