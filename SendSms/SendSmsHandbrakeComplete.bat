::ECHO OFF
d:
cd \Users\rgw3\PythonScripts\SendSms

SET quoted=%1
SET unquoted=%quoted:"='%

py LogHandbrake.pyw "Handbrake completed %unquoted:"='%"

::pause

