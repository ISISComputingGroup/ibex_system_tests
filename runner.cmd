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
 -suites AllTests ^
 -testOptions "testExecTimeout=3600" ^
 -autVMArgs "-Xms64m;-Xmx2048m;-XX:MaxPermSize=512m" ^
 -timeout 18000
