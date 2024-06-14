; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppVersion "0.906"
#define MyAppName "EcuapassBot"
#define MyAppExeName "EcuapassBot.bat"
#define MyAppIconFile "EcuapassBot.ico"
#define MyInstallerName "EcuapassBot-0906-Instalador"

#define MyAppPublisher "Software Inteligente"
#define MyAppURL "https://www.softwareinteligente.co"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{EC8C5773-A046-402D-B9B8-2222E0B3429B}
AppName="EcuapassBot"
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\EcuapassBot
;DefaultDirName={autopf}\
DisableDirPage=yes
DisableProgramGroupPage=yes
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputBaseFilename={#MyInstallerName}
Compression=zip
SolidCompression=yes
WizardStyle=modern
; Other setup options...

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "resources\test\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "resources\ecuapass_app\*"; DestDir: "{app}\{#MyAppName}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name:"{autoprograms}\{#MyAppName}"; Filename:"{app}\{#MyAppExeName}"; Parameters: "/minimized"; Flags: runminimized; IconFilename:"{app}\{#MyAppIconFile}"; IconIndex:0; Tasks: desktopicon
Name:"{autodesktop}\{#MyAppName}"; Filename:"{app}\{#MyAppExeName}"; Parameters: "/minimized"; Flags: runminimized;  IconFilename:"{app}\{#MyAppIconFile}"; IconIndex:0; Tasks: desktopicon

[Run]
Filename: "{app}\FirstUpdate.bat"; Description: "Actualizar"; Flags: postinstall runasoriginaluser
;Filename: "{app}\EcuapassBot.bat"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent; \


