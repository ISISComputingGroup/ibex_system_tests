set MYDIRBLOCK=%~dp0

REM the password for isis\builder is contained in the BUILDERPW system environment variable on the build server
REM we map this early as some other stuff (e.g. CSS, DAE DLLs) is copied from \\isis\inst$ too during build 
net use p: /d
net use p: \\isis\inst$ /user:isis\builder %BUILDERPW%

REM Delete simulated instrument
rd /S /Q "C:\data"
mkdir "C:\data"

REM Install genie_python, deleting the old one first, and going back to the workspace that the installer moves from
rd /S /Q "C:\Instrument\Apps\Python\"
call "\\isis\inst$\Kits$\CompGroup\ICP\Client\genie_python\genie_python_install.bat"
cd %WORKSPACE%

REM Clean up the previous versions
rd /S /Q "C:\Instrument\Apps\EPICS\"

REM Delete old configuration directory
rd /S /Q "C:\Instrument\Settings\"
rd /S /Q "C:\Instrument\Var\"

REM Clean up the previous version of the GUI
rd /S /Q "ibex_gui"

REM Get the latest versions via a Python script
c:\Python27\python.exe get_latest_builds.py
if %errorlevel% neq 0 exit /b %errorlevel%

call "C:\Instrument\Apps\EPICS\create_icp_binaries"
runas.exe /user:administrator c:\Instrument\Apps\EPICS\ICP_Binaries\isisdae\x64\Release\isisicp.exe /RegServer
runas.exe /user:administrator c:\Instrument\Apps\EPICS\ICP_Binaries\isisdae\x64\Release\isisdatasvr.exe /RegServer

REM Start the instrument
call "C:\Instrument\Apps\EPICS\start_inst.bat"

REM Sleep for 120 s while start ups finalise
ping 127.0.0.1 -n 120 > nul

call runner.cmd

cd EPICS
call "C:\Instrument\Apps\EPICS\stop_inst.bat"

REM Sleep for 120 s while shut downs finalise
ping 127.0.0.1 -n 120 > nul
