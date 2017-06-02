setlocal

@echo off

call %~dp0get_builds.bat
if %errorlevel% neq 0 exit /b %errorlevel%

REM Run config_env
REM call "C:\Instrument\Apps\EPICS\config_env"

REM Get the icp binaries so that the DAE can run
REM call "C:\Instrument\Apps\EPICS\create_icp_binaries"

rmdir /q /s test-reports

call "C:\Instrument\Apps\EPICS\support\IocTestFramework\master\run_all_tests.bat"
if %errorlevel% neq 0 exit /b %errorlevel%

REM cleanup

call "C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
@taskkill /f /im javaw.exe /t
@taskkill /f /im pythonw.exe /t
@taskkill /f /im ibex-client.exe /t

net use p: /d
net use \\shadow.isis.cclrc.ac.uk /d

REM Sleep for 120 s while shut downs finalise
sleep 120