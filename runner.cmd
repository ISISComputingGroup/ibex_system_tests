SET AUT=C:\Instrument\Dev\Client\ibex_gui\base\uk.ac.stfc.isis.ibex.client.product\target\products\ibex.product\win32\win32\x86_64
SET RUNNER=C:\Instrument\Dev\System_Test\runner
SET PROJECT=C:\Instrument\Dev\System_Test\IBEX_System_Tests

SET RESULTS=C:\Instrument\Dev\System_Test\Results

IF NOT EXIST %RESULTS% GOTO NORESULTS
RMDIR /S /Q %RESULTS%

:NORESULTS
md %RESULTS%

java -jar %RUNNER%/plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar ^
 -application org.eclipse.rcptt.runner.headless ^
 -data %RESULTS%/runner-workspace/ ^
 -aut %AUT% ^
 -autWsPrefix %RESULTS%/aut-workspace ^
 -autConsolePrefix %RESULTS%/aut-output ^
 -htmlReport %RESULTS%/report.html ^
 -junitReport %RESULTS%/report.xml ^
 -import %PROJECT% 