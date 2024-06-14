:: Create executable from python script
::rmdir /S /Q last
::mkdir last
::move build last
::move dist last
::move *.spec last
::move *.exe last
set GUIPATH=data/ecuapassgui
set RESPATH=ecupassdocs/resources
set APPPATH=data/ecuapass_app.py

pyinstaller --add-data "data/resources/*";"./" --add-data "data/ecuapassdocs/resources/data_cartaportes/*.txt";"ecuapassdocs/resources/data_cartaportes/" --add-data "data/ecuapassdocs/resources/data_manifiestos/*.txt";"ecuapassdocs/resources/data_manifiestos/" --add-data "data/ecuapassdocs/resources/docs/*.png";"ecuapassdocs/resources/docs/" --add-data "data/ecuapassdocs/resources/docs/*.pdf";"ecuapassdocs/resources/docs/" --add-data "data/ecuapassdocs/resources/docs/*.json";"ecuapassdocs/resources/docs/" data/ecuapass_app.py

::pyinstaller data/test.py

::pyinstaller --add-data "data/resources/*";"./" --add-data "data/ecuapassdocs/resources/images;images" --add-data "data/ecuapassdocs/resources/data_cartaportes/*.txt";"ecuapassdocs/resources/data_cartaportes/" --add-data "data/ecuapassdocs/resources/data_manifiestos/*.txt";"ecuapassdocs/resources/data_manifiestos/" --add-data "data/ecuapassdocs/resources/docs/*.png";"ecuapassdocs/resources/docs/" --add-data "data/ecuapassdocs/resources/docs/*.pdf";"ecuapassdocs/resources/docs/" --add-data "data/ecuapassdocs/resources/docs/*.json";"ecuapassdocs/resources/docs/" data/ecuapass_app.py

::copy dist\*.exe .
