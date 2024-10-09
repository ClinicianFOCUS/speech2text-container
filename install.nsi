;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Docker Compose Installer"
  OutFile "DockerComposeInstaller.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\DockerCompose"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\DockerCompose" ""

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\Modern UI\License.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Docker Compose" SecDockerCompose

  SetOutPath "$INSTDIR"

  ; Download and install Docker Compose
  inetc::get "https://github.com/docker/compose/releases/latest/download/docker-compose-Windows-x86_64.exe" "$INSTDIR\docker-compose.exe"
  Pop $0
  StrCmp $0 "OK" +3
    MessageBox MB_OK "Failed to download Docker Compose: $0"
    Abort

  ; Copy docker-compose.yml from the repository
  File "docker-compose.yml"

  ; Run Docker Compose
  ExecWait '"$INSTDIR\docker-compose.exe" -f "$INSTDIR\docker-compose.yml" up -d'

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDockerCompose ${LANG_ENGLISH} "Install Docker Compose and run the Docker Compose file."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDockerCompose} $(DESC_SecDockerCompose)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ; Remove Docker Compose and docker-compose.yml
  Delete "$INSTDIR\docker-compose.exe"
  Delete "$INSTDIR\docker-compose.yml"

  ; Remove installation directory
  RMDir "$INSTDIR"

  ; Remove registry key
  DeleteRegKey /ifempty HKCU "Software\DockerCompose"

SectionEnd
