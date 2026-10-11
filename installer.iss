; ImageViewer Windows installer (Inno Setup 6)
; Build via build-installer.bat. Requires PyInstaller (for the onedir exe)
; and Inno Setup 6's ISCC.exe on the build machine.

#define MyAppName "画像ビューアー"
#define MyAppExeName "ImageViewer.exe"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "kairamu"
#define MyAppProgId "ImageViewer.Image"

[Setup]
; Keep this AppId stable across versions so upgrades replace, not duplicate.
AppId={{B2F1C3A4-5D6E-47F8-9A0B-1C2D3E4F5A6B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\ImageViewer
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Per-user install so no administrator/UAC prompt is needed.
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=ImageViewer-Setup-{#MyAppVersion}
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associate"; Description: "対応画像の「プログラムから開く」に画像ビューアーを追加する"; Flags: unchecked

[Files]
; The whole PyInstaller --onedir output (ImageViewer.exe + _internal\...).
Source: "dist\ImageViewer\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; A ProgID describing "open an image with ImageViewer". Registered under the
; user's hive (HKA -> HKCU for a per-user install); does NOT force the app as
; the default handler -- it only adds it to the "Open with" list / Default Apps.
Root: HKA; Subkey: "Software\Classes\{#MyAppProgId}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppName} 画像"; Flags: uninsdeletekey; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#MyAppProgId}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#MyAppProgId}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associate
; Offer the ProgID for each supported extension (matches SUPPORTED_EXTS).
Root: HKA; Subkey: "Software\Classes\.jpg\OpenWithProgids";  ValueType: string; ValueName: "{#MyAppProgId}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.jpeg\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppProgId}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.png\OpenWithProgids";  ValueType: string; ValueName: "{#MyAppProgId}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.bmp\OpenWithProgids";  ValueType: string; ValueName: "{#MyAppProgId}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.gif\OpenWithProgids";  ValueType: string; ValueName: "{#MyAppProgId}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.webp\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppProgId}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.tiff\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppProgId}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.tif\OpenWithProgids";  ValueType: string; ValueName: "{#MyAppProgId}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
