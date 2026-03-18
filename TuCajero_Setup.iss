; TuCajero POS Installer Script
; Generated for Inno Setup 6.x

#define MyAppName "TuCajero POS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Ing. Francisco Llinas P."
#define MyAppURL "mailto:cruzmedicdrogueria@gmail.com"
#define MyAppExeName "TuCajero.exe"

[Setup]
; Application info
AppId={{A5F2E8D1-7C3B-4E9F-8A2D-5B6C7E8F9A0B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppContact={#MyAppURL}

; Install locations
DefaultDirName={autopf}\TuCajero
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
AllowNoIcons=yes

; Output settings
OutputDir=installer
OutputBaseFilename=TuCajero_Setup_v{#MyAppVersion}
SetupIconFile=tucajero\assets\icons\cruzmedic.ico
Compression=lzma2/ultra64
SolidCompression=yes

; Privileges - lowest for normal user installation
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; UI settings
WizardStyle=modern

; Uninstall settings
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} v{#MyAppVersion}

; Version info
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Instalador TuCajero POS
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; Architecture
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"
Name: "startmenuicon"; Description: "Crear acceso directo en el menu inicio"; GroupDescription: "Opciones adicionales:"

[Files]
Source: "dist\TuCajero.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commonstartmenu}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName} ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// Pre-install cleanup
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Ask user if they want to remove app data
    if MsgBox('¿Desea eliminar todos los datos de TuCajero?' + #13#10 +
              '(Base de datos, configuraciones, logs)', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      AppDataPath := ExpandConstant('{localappdata}\TuCajero');
      if DirExists(AppDataPath) then
        DelTree(AppDataPath, True, True, True);
    end;
  end;
end;

// Check if app is running before install
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Check if TuCajero is running
  if Exec('tasklist', '/FI "IMAGENAME eq TuCajero.exe" /NH', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    // App might be running, warn user
  end;
end;
