setlocal
SET AUT=%WORKSPACE%\ibex_gui\Client
SET RUNNER=C:\Jenkins\RCPTT_Runner
SET PROJECT=%WORKSPACE%

SET RESULTS=%WORKSPACE%\Results

IF NOT EXIST %RESULTS% GOTO NORESULTS
RMDIR /S /Q %RESULTS%

:NORESULTS
md %RESULTS%

java -jar %RUNNER%\plugins\org.eclipse.equinox.launcher_1.3.200.v20160318-1642.jar ^
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
