#define MyAppName "EasyFeet"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#ifndef DistBundle
  #define DistBundle "..\dist\EasyFeet"
#endif
#define MyAppPublisher "EasyFeet"
#define MyAppExeName "EasyFeet.exe"

[Setup]
AppId={{A2B4C4D9-8A8B-4E37-8E58-89A7A9C68E31}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\EasyFeet
DefaultGroupName=EasyFeet
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=EasyFeet-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Files]
Source: "{#DistBundle}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\EasyFeet"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\EasyFeet"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar EasyFeet"; Flags: nowait postinstall skipifsilent
