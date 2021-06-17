::ECHO OFF


IF "%1" == "" OR "%2" == "" GOTO Usage

py SendSms.py %1 \"%2\"
GOTO End 

:Usage
ECHO USAGE: SendSms.bat 4075551212 "Message text"
GOTO End

:End