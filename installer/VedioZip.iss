#define MyAppName "VedioZip"
#define MyAppPublisher "Abladol"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

[Setup]
AppId={{BF257E7B-8C64-4F78-96E0-9A26A8C81589}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=VedioZip-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "..\dist\VedioZip.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\ffprobe.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\VedioZip.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\VedioZip.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\VedioZip.exe"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
