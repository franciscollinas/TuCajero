[Setup]
AppName=TuCajero POS
AppVersion=1.0
AppVerName=TuCajero POS v1.0
AppPublisher=Droguería CruzMedic
AppPublisherURL=mailto:cruzmedicdrogueria@gmail.com
AppSupportURL=mailto:cruzmedicdrogueria@gmail.com
AppContact=cruzmedicdrogueria@gmail.com
DefaultDirName={autopf}\TuCajero
DefaultGroupName=TuCajero POS
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=TuCajero_Setup_v1.0
SetupIconFile=tucajero\assets\icons\cruzmedic.ico
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\TuCajero.exe
UninstallDisplayName=TuCajero POS v1.0
VersionInfoVersion=1.0.0.0
VersionInfoCompany=Droguería CruzMedic
VersionInfoDescription=Sistema POS TuCajero
VersionInfoProductName=TuCajero POS
VersionInfoProductVersion=1.0
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"
Name: "startmenuicon"; Description: "Crear acceso directo en el menú inicio"; GroupDescription: "Opciones adicionales:"

[Files]
Source: "dist\TuCajero.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\TuCajero POS"; Filename: "{app}\TuCajero.exe"; IconFilename: "{app}\TuCajero.exe"
Name: "{group}\Desinstalar TuCajero"; Filename: "{uninstallexe}"
Name: "{commondesktop}\TuCajero POS"; Filename: "{app}\TuCajero.exe"; Tasks: desktopicon
Name: "{commonstartmenu}\TuCajero POS"; Filename: "{app}\TuCajero.exe"; Tasks: startmenuicon

[Run]
Filename: "{app}\TuCajero.exe"; Description: "Iniciar TuCajero POS ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
