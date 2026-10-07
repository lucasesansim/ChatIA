#define MyAppVersion "0.1.0"
[Setup]
AppId={{3B735CBD-4AAC-4BC5-BB30-614D21D116A4}
AppName=ChatIA
AppVersion={#MyAppVersion}
AppPublisher=ChatIA contributors
DefaultDirName={localappdata}\Programs\ChatIA
DefaultGroupName=ChatIA
PrivilegesRequired=lowest
OutputDir=..\..\dist
OutputBaseFilename=ChatIA-{#MyAppVersion}-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\ChatIA.exe
LicenseFile=..\..\LICENSE

[Files]
Source: "..\..\dist\ChatIA\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ChatIA"; Filename: "{app}\ChatIA.exe"

[Run]
Filename: "{app}\ChatIA.exe"; Description: "Abrir ChatIA"; Flags: nowait postinstall skipifsilent
