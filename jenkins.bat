md EPICS
copy "\\isis\inst$\Kits$\CompGroup\ICP\EPICS\EPICS_CLEAN_win7_x64\BUILD-1101*" EPICS

cd EPICS
call start_inst.bat
TIMEOUT 120
cd ../

md ibex_gui
copy "\\isis\inst$\Kits$\CompGroup\ICP\Client\BUILD402\Client" ibex_gui

call runner.cmd

call stop_inst.bat
TIMEOUT 120
