JARPATH=/home/lg/BIO/iaprojects/ecuapassdocs/ecuapassdocs-botpy/ecugui/store/EcuapassDocsGUI.jar
jpackage --type app-image --input EcuapassDocsGUI.jar --main-jar $JARPATH --name EcuapassDocsGUI --main-class main.MainController --dest /tmp --verbose
