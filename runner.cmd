setlocal
SET AUT=%WORKSPACE%\ibex_gui\Client

REM v2.1.0
SET RUNNER=C:\Jenkins\Runner\rcptt.ide-2.1.0-win32.win32.x86_64\rcptt
SET LAUNCHER=1.3.200.v20160318-1642

REM a v2.2.0 nightly snapshot
SET RUNNER=C:\Jenkins\Runner\rcptt.ide-2.2.0-N201701070024-win32.win32.x86_64\rcptt
SET LAUNCHER=1.3.201.v20161025-1711

SET PROJECT=%WORKSPACE%

SET RESULTS=%WORKSPACE%\Results

IF NOT EXIST %RESULTS% GOTO NORESULTS
RMDIR /S /Q %RESULTS%
if exist "%RESULTS%" (
    timeout /t 10 /nobreak >NUL
    rd /S /Q %RESULTS%
)

:NORESULTS
md %RESULTS%

java -jar %RUNNER%\plugins\org.eclipse.equinox.launcher_%LAUNCHER%.jar ^
 -application org.eclipse.rcptt.runner.headless ^
 -data %RESULTS%\runner-workspace\ ^
 -aut %AUT% ^
 -autWsPrefix %RESULTS%\aut-workspace ^
 -autConsolePrefix %RESULTS%\aut-output ^
 -htmlReport %RESULTS%\report.html ^
 -junitReport %RESULTS%\report.xml ^
 -import %PROJECT% ^
 -suites %1% ^
 -testOptions "testExecTimeout=3600;passedTestDetails=true;launchingKillAutOnConnectError=true" ^
 -autVMArgs "-Xms64m;-Xmx3g;-XX:+UseG1GC" ^
 -timeout 18000

REM had some GC overhead limit exceeded errors, trying G1GC but
REM may need to use concat mark sweep with check disabled
REM -XX:+UseConcMarkSweepGC
REM -XX:-UseGCOverheadLimit 
REM for debugging use
REM -XX:+PrintGCDetails -XX:+PrintGCTimeStamps
