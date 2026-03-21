#define MyAppName "TuCajero POS"
#define MyAppVersion "3.0"
#define MyAppPublisher "Droguería CruzMedic"
#define MyAppURL "mailto:cruzmedicdrogueria@gmail.com"
#define MyAppExeName "TuCajero.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{E6A0F1B2-C1D2-4E3F-B4A5-F6G7H8I9J0K1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppContact={#MyAppURL}
DefaultDirName={autopf}\TuCajero
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=TuCajero_Setup_v3.0
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} v{#MyAppVersion}
VersionInfoVersion=3.0.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Sistema POS TuCajero
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"
Name: "startmenuicon"; Description: "Crear acceso directo en el menú inicio"; GroupDescription: "Opciones adicionales:"

[Files]
Source: "dist\TuCajero.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar TuCajero"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commonstartmenu}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName} ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\TuCajero"
Type: filesandordirs; Name: "{app}"
