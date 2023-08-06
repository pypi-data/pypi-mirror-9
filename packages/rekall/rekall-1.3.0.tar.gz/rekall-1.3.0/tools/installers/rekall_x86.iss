#define WINPMEM_VERSION '1.6.2'
#define REKALL_VERSION '1.2.1'
#define REKALL_CODENAME 'Col de la Croix'

[Files]
; Extra Binaries to add to the package.
Source: C:\Python27.32\Lib\site-packages\distorm3\distorm3.dll; DestDir: {app}\dlls
; Source: C:\Python27.32\DLLs\libyara.dll; DestDir: {app}\dlls
Source: C:\Windows\system32\MSVCR100.dll; DestDir: {app}
Source: C:\Windows\system32\MSVCP100.dll; DestDir: {app}

; Winpmem tool
Source: ..\windows\winpmem\winpmem_{#WINPMEM_VERSION}.exe; DestDir: {app}
Source: ..\windows\winpmem\winpmem_write_{#WINPMEM_VERSION}.exe; DestDir: {app}

; PyInstaller files.
DestDir: {app}; Source: ..\..\dist\rekal\*; Excludes: "_MEI"; Flags: recursesubdirs

; Manuscript files for webconsole
DestDir: {app}\manuskript\; Source: ..\..\manuskript\*; Flags: recursesubdirs
DestDir: {app}\webconsole\; Source: ..\..\rekall\plugins\tools\webconsole\*; Flags: recursesubdirs

[Setup]
Compression=zip
AppCopyright=GPLv2
AppPublisher=Rekall Team
AppPublisherURL=http://www.rekall-forensic.com/
AppName=Rekall
AppVerName=Rekall v{#REKALL_VERSION} {#REKALL_CODENAME}
DefaultDirName={pf}\Rekall
VersionInfoVersion={#REKALL_VERSION}
; ArchitecturesAllowed=x86
VersionInfoCompany=Rekall Inc.
VersionInfoDescription=Rekall Memory Forensic Framework
VersionInfoCopyright=Rekall Developers.
VersionInfoProductName=Rekall Memory Forensic Framework
MinVersion=5.01.2600sp1
PrivilegesRequired=poweruser
TimeStampsInUTC=true
OutputBaseFilename=Rekall_{#REKALL_VERSION}_{#REKALL_CODENAME}_x86
VersionInfoTextVersion=Rekall Memory Forensic Framework
InfoAfterFile=..\..\README.md
LicenseFile=..\..\LICENSE.txt
AllowNoIcons=true
AlwaysUsePersonalGroup=true
DefaultGroupName=Rekall Memory Forensics
SetupIconFile=..\..\resources\rekall.ico
UninstallDisplayIcon={app}\rekall.exe

[_ISTool]
UseAbsolutePaths=true

[Icons]
Name: {group}\{cm:UninstallProgram, Rekall}; Filename: {uninstallexe}
Name: {group}\Rekall Memory Forensics (Console); Filename: {app}\Rekal.exe; WorkingDir: {app}
Name: {group}\Rekall Memory Forensics (Notebook); Filename: {app}\Rekal.exe; WorkingDir: {app}; Parameters: notebook
Name: {group}\Rekall Documentation; Filename: http://www.rekall-forensic.com/docs.html
