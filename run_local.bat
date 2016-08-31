REM Delete simulated instrument
rd /S /Q "C:\data"

REM Delete old configuration directory
rd /S /Q "C:\Instrument\Settings\"

REM Start the instrument
call "C:\Instrument\Apps\EPICS\start_ibex_server.bat"

REM Sleep for 120 s while start ups finalise
ping 127.0.0.1 -n 120 > nul

call runner.cmd

cd "C:\Instrument\Apps\EPICS"
call "C:\Instrument\Apps\EPICS\stop_ibex_server.bat"

REM Sleep for 120 s while shut downs finalise
ping 127.0.0.1 -n 120 > nul
