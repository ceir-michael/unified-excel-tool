@echo off
setlocal
cd /d "%~dp0\.."

set "BUILD_VENV=.build-venv"

if not exist "%BUILD_VENV%\Scripts\python.exe" (
    where py >nul 2>nul
    if errorlevel 1 (
        python -m venv "%BUILD_VENV%" || exit /b 1
    ) else (
        py -3.12 -m venv "%BUILD_VENV%" || exit /b 1
    )
)

"%BUILD_VENV%\Scripts\python.exe" -m pip install --upgrade pip || exit /b 1
"%BUILD_VENV%\Scripts\python.exe" -m pip install -r requirements-build.txt || exit /b 1
"%BUILD_VENV%\Scripts\python.exe" -m PyInstaller --noconfirm --clean build\UnifiedExcelTools.spec || exit /b 1

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ISCC%" (
    for /f "delims=" %%V in ('%BUILD_VENV%\Scripts\python.exe -c "import constants; print(constants.APP_VERSION)"') do set "APP_VERSION=%%V"
    "%ISCC%" /DMyAppVersion="%APP_VERSION%" build\installer.iss || exit /b 1
    echo Installer created in dist\installer.
) else (
    echo Application created in dist\UnifiedExcelTools.
    echo Install Inno Setup 6 to also create a single Windows installer.
)

endlocal
