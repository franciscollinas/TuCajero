[Setup]
AppName=TuCajero POS
AppVersion=3.0
AppVerName=TuCajero POS v3.0
AppPublisher=Droguería CruzMedic
AppPublisherURL=mailto:cruzmedicdrogueria@gmail.com
AppSupportURL=mailto:cruzmedicdrogueria@gmail.com
AppContact=cruzmedicdrogueria@gmail.com
LicenseFile=Licencia.txt
UserInfoPage=yes
DefaultDirName={autopf}\TuCajero
DefaultGroupName=TuCajero POS
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=TuCajero_Setup_v3.0
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\TuCajero.exe
UninstallDisplayName=TuCajero POS v3.0
VersionInfoVersion=3.0.0.0
VersionInfoCompany=Droguería CruzMedic
VersionInfoDescription=Sistema POS TuCajero
VersionInfoProductName=TuCajero POS
VersionInfoProductVersion=3.0
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
Type: filesandordirs; Name: "{localappdata}\TuCajero"
Type: filesandordirs; Name: "{app}"

[Code]
// Función que valida el Número de Serie durante la instalación
function CheckSerial(Serial: String): Boolean;
begin
  // El Código de Serie por defecto para la v3.0
  // Puedes cambiar este valor según necesites
  Result := (Serial = 'TUCAJERO-30-OFFICIAL-2026');
end;

