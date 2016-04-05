md EPICS

REM the password for isis\builder is contained in the BUILDERPW system environment variable on the build server
REM we map this early as some other stuff (e.g. CSS, DAE DLLs) is copied from \\isis\inst$ too during build 
net use p: /d
net use p: \\isis\inst$ /user:isis\builder %BUILDERPW%

XCOPY "\\isis\inst$\Kits$\CompGroup\ICP\EPICS\EPICS_CLEAN_win7_x64\BUILD-1101" EPICS /C /S /D /Y /I

REM Delete old configuration directory
RMDIR "C:\Instrument\Settings\config\NDWRENO" /S /Q

cd EPICS
call start_inst.bat
ping 127.0.0.1 -n 120 > nul
cd ../

md ibex_gui
XCOPY "C:\Users\builder\Desktop\ibex.product-win32.win32.x86_64" ibex_gui /C /S /D /Y /I

call runner.cmd

call stop_inst.bat
ping 127.0.0.1 -n 6 > nul
