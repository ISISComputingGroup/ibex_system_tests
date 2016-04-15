REM the password for isis\builder is contained in the BUILDERPW system environment variable on the build server
REM we map this early as some other stuff (e.g. CSS, DAE DLLs) is copied from \\isis\inst$ too during build 
net use p: /d
net use p: \\isis\inst$ /user:isis\builder %BUILDERPW%

REM Install genie_python, deleting the old one first, and going back to the workspace that the installer moves from
rd /S /Q "C:\Instrument\Apps\Python\"
call "\\isis\inst$\Kits$\CompGroup\ICP\Client\genie_python\genie_python_install.bat"
cd %WORKSPACE%

REM Copy over most recent EPICS build
rd /S /Q "C:\Instrument\Apps\EPICS\"
XCOPY "\\isis\inst$\Kits$\CompGroup\ICP\EPICS\EPICS_win7_x64\BUILD_LATEST" "C:\Instrument\Apps\EPICS" /C /S /D /Y /I

REM Delete old configuration directory
rd /S /Q "C:\Instrument\Settings\"
rd /S /Q "C:\Instrument\Var\"

REM Start the instrument
call "C:\Instrument\Apps\EPICS\start_inst.bat"

REM Sleep for 120 s while start ups finalise
ping 127.0.0.1 -n 120 > nul

REM Copy accross the most recent version of the GUI
rd /S /Q "ibex_gui"
md ibex_gui
XCOPY "\\isis\inst$\Kits$\CompGroup\ICP\Client\BUILD_LATEST\Client" ibex_gui /C /S /D /Y /I

call runner.cmd

cd EPICS
call "C:\Instrument\Apps\EPICS\stop_inst.bat"

REM Sleep for 120 s while shut downs finalise
ping 127.0.0.1 -n 120 > nul
