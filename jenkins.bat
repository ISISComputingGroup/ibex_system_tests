setlocal

REM the password for isis\builder is contained in the BUILDERPW system environment variable on the build server
REM we map this early as some other stuff (e.g. CSS, DAE DLLs) is copied from \\isis\inst$ too during build 
net use p: /d
net use p: \\isis\inst$ /user:isis\builder %BUILDERPW%

REM is previous system tests aborted, we may still have processes running
if exist "C:\Instrument\Apps\EPICS\stop_ibex_server.bat" (
    call "C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
)
@taskkill /f /im javaw.exe /t
@taskkill /f /im pythonw.exe /t
@taskkill /f /im ibex-client.exe /t

REM Delete simulated instrument
rd /S /Q "C:\data"
mkdir "C:\data"

REM Install genie_python, deleting the old one first, and going back to the workspace that the installer moves from
rd /S /Q "C:\Instrument\Apps\Python\"

call "\\isis\inst$\Kits$\CompGroup\ICP\Client\genie_python\genie_python_install.bat"
if %errorlevel% neq 0 exit /b %errorlevel%

cd %WORKSPACE%

REM Clean up the previous versions
rd /S /Q "C:\Instrument\Apps\EPICS\"
if exist "C:\Instrument\Apps\EPICS\" rd /S /Q "C:\Instrument\Apps\EPICS\"

REM Delete old configuration directory
rd /S /Q "C:\Instrument\Settings\"
rd /S /Q "C:\Instrument\Var\"

REM Clean up the previous version of the GUI
rd /S /Q "ibex_gui"
if exist "ibex_gui" rd /S /Q "ibex_gui"

REM Get the latest versions via a Python script
c:\Python27\python.exe get_latest_builds.py
if %errorlevel% neq 0 exit /b %errorlevel%

REM Run config_env
call "C:\Instrument\Apps\EPICS\config_env"

REM Get the icp binaries so that the DAE can run
call "C:\Instrument\Apps\EPICS\create_icp_binaries"

REM Start the instrument
call "C:\Instrument\Apps\EPICS\start_ibex_server.bat"

REM Sleep for 120 s while start ups finalise
sleep 120

cd %~dp0
call runner.cmd

call "C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
@taskkill /f /im javaw.exe /t
@taskkill /f /im pythonw.exe /t
@taskkill /f /im ibex-client.exe /t

REM Sleep for 120 s while shut downs finalise
sleep 120
