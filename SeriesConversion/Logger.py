import sys
import os
import datetime


class Logger:

    def __init__(self, logPath):
        self.logPath = logPath


    def AddError(self, message: str, displayToConsole:bool=True, prependNewline:bool=False, appendNewline:bool=False):
        self.__WriteEntry__('e', message, displayToConsole, prependNewline=prependNewline, appendNewline=appendNewline)

    def AddInfo(self, message: str, displayToConsole:bool=True, prependNewline:bool=False, appendNewline:bool=False):
        self.__WriteEntry__('i', message, displayToConsole, prependNewline=prependNewline, appendNewline=appendNewline)

    def AddWarning (self, message: str, displayToConsole:bool=True, prependNewline:bool=False, appendNewline:bool=False):
        self.__WriteEntry__('w', message, displayToConsole, prependNewline=prependNewline, appendNewline=appendNewline)


    def __WriteEntry__(self, messageType: str, message: str, displayToConsole: bool, prependNewline:bool=False, appendNewline:bool=False):

        now = datetime.datetime.now()

        prefix = 'UNKNOWN'
        if messageType == 'e': prefix = 'ERROR  '
        elif messageType == 'i': prefix = 'INFO   '
        elif messageType == 'w': prefix = 'WARNING'

        if displayToConsole: 
            if prependNewline: print('\n')
            print(f'{prefix} - {message}')
            if appendNewline: print('\n')

        log = None
        try:
            log = open(self.logPath, 'a')

            log.write(f'{now:%Y-%m-%d %H:%M} - {prefix} - {message}\n')

        except:
            print(f'ERROR - unable to write log file {self.logPath}\n')

        finally:
            if log is not None and not log.closed:
                log.close()
