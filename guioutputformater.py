import os

from commandprice import CommandPrice
from abstractoutputformater import AbstractOutputFormater
from datetimeutil import DateTimeUtil


class GuiOutputFormater(AbstractOutputFormater):
    
    
    def __init__(self, configurationMgr, activateClipboard = False):
        '''
        Ctor. The parm activateClipboard with default value set to False was added to prevent SeqDiagBuilder
        unit tests in TestSeqDiagBuilder where the CryptoPricer Condtroller class were implied to crash the Pycharm
        unit test environment. This crask was due to an obscure problem in the Pycharm unit test framework. This
        failure only happened if the kivy clipboard class was imported.

        :param configurationMgr:
        :param activateClipboard:
        '''
        # commented code below does not run in Pydroid since Pydroid does not support
        # the sl4a lib
        # if os.name == 'posix':
        #     import android
        #     self._clipboard = android.Android()
        # else:
        self.activateClipboard = activateClipboard

        if self.activateClipboard:
            from kivy.core.clipboard import Clipboard
            self._clipboard = Clipboard

        self.configurationMgr = configurationMgr


    def printDataToConsole(self, resultData):
        '''
        print the result to the console and 
        paste it to the clipboard
        '''
        outputStr = super(GuiOutputFormater, self).getPrintableData(resultData)
                                        	                                  	
        print(outputStr)
        
        
    def getFullCommandString(self, resultData):
        '''
        Recreate the full command string corresponding to a full or partial price request entered by the user.

        The full command string contains a full date and time which is formatted according to the date time
        format as specified in the configuration file. Even if the request only contained partial date time info,
        the full command string ccontains a full date time specification.

        The full command string will be stored in the command history list so it can be replayed or saved to file.
        An empty string is returned if the command generated an error (empty string will not be added to history !

        In case an option to the command with save mode is in effect - for example -vs -, then the full
        command with the save mode option is returned aswell. Othervise, if no command option in save mode
        is in effect (no option or -v for example), then None is returned as second return value.

        :param resultData: result of the last full or partial request
        :seqdiag_return printResult, fullCommandStr, fullCommandStrWithOptions, fullCommandStrWithSaveModeOptions
        :return: 1/ full command string with no command option corresponding to a full or partial price request
                    entered by the user or empty string if the command generated an error msg.
                 2/ full request command with any non save command option
                 3/ full command string with command option in save mode or none if no command option in save mode
                    is in effect or if the command option generated a warning.

                 Ex: 1/ eth usd 0 bitfinex
                     2/ None
                     3/ eth usd 0 bitfinex -vs0.1eth

                     1/ eth usd 0 bitfinex
                     2/ eth usd 0 bitfinex -v0.1btc (even if warning generated !)
                     3/ None (-v0.1btc command was entered, which generated a warning)

                     1/ eth usd 0 bitfinex
                     2/ None (no value command in effect)
                     3/ None (no value command with save option in effect)
        '''
        if resultData.isError():
            return '', None, None
            
        commandDic = resultData.getValue(resultData.RESULT_KEY_INITIAL_COMMAND_PARMS)
        priceType = resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE)
        
        if priceType == resultData.PRICE_TYPE_RT:      
            fullCommandStr = commandDic[CommandPrice.CRYPTO] + ' ' + \
                             commandDic[CommandPrice.FIAT] + ' 0 ' + \
                             commandDic[CommandPrice.EXCHANGE]
        else:
            requestDateDMY, requestDateHM = self._buildFullDateAndTimeStrings(commandDic, self.configurationMgr.localTimeZone)

            fullCommandStr = commandDic[CommandPrice.CRYPTO] + ' ' + \
                             commandDic[CommandPrice.FIAT] + ' ' + \
                             requestDateDMY + ' ' + \
                             requestDateHM + ' ' + \
                             commandDic[CommandPrice.EXCHANGE]

        fullCommandStrWithSaveModeOptions = None
        fullCommandStrWithOptions = None

        if resultData.getValue(resultData.RESULT_KEY_PRICE_VALUE_SAVE):
            if not resultData.containsWarning(resultData.WARNING_TYPE_COMMAND_VALUE):
                #in case the value command generated a warning, if the value command data contains a crypto or fiat
                #different from the crypto or fiat of tthe request, the fullCommandStrWithSaveModeOptions remains
                #None and wont't be stored in the request history list of the GUI !
                fullCommandStrWithSaveModeOptions = fullCommandStr + ' -vs' + commandDic[CommandPrice.PRICE_VALUE_AMOUNT] + commandDic[CommandPrice.PRICE_VALUE_SYMBOL]
        else:
            valueCommandAmountStr = commandDic[CommandPrice.PRICE_VALUE_AMOUNT]
            valueCommandSymbolStr = commandDic[CommandPrice.PRICE_VALUE_SYMBOL]
            if valueCommandAmountStr and valueCommandSymbolStr:
                #even in case the value command generated a warning, it will be displayed in the status bar !
                fullCommandStrWithOptions = fullCommandStr + ' -v' + valueCommandAmountStr + valueCommandSymbolStr

        from seqdiagbuilder import SeqDiagBuilder
        SeqDiagBuilder.recordFlow()

        return fullCommandStr, fullCommandStrWithOptions, fullCommandStrWithSaveModeOptions


    def _buildFullDateAndTimeStrings(self, commandDic, timezoneStr):
        '''
        This method ensures that the full command string is unified whatever the completness of the
        dated/time components specified in the request by the user.

        Ex: btc usd 1/1 bitfinex or btc usd 1/01/18 bitfinex or btc usd 1/1 12:23 bitfinex all return
            a full commaand of btc usd 01/01/18 00:00 bitfinex, btc usd 01/01/18 12:23 bitfinex
            respectively.

        This is important since the ful command string is what is stored in the command history list, with
        no duplicates. Otherwxise, btc usd 1/1 00:00 bitfinex and btc usd 01/01/18 00:00 bitfinex would
        be stored as 2 entries !

        :param commandDic:
        :param timezoneStr:
        :seqdiag_return requestDateDMY, requestDateHM
        :return:
        '''
        dayInt = int(commandDic[CommandPrice.DAY])
        monthInt = int(commandDic[CommandPrice.MONTH])
        year = commandDic[CommandPrice.YEAR]

        if year == None:
            now = DateTimeUtil.localNow(timezoneStr)
            yearInt = now.year
        else:
            yearInt = int(year)

        hour = commandDic[CommandPrice.HOUR]
        minute = commandDic[CommandPrice.MINUTE]

        if hour != None and minute != None:
            # hour can not exist without minute and vice versa !
            hourInt = int(hour)
            minuteInt = int(minute)
        else:
            hourInt = 0
            minuteInt = 0

        requestArrowDate = DateTimeUtil.dateTimeComponentsToArrowLocalDate(dayInt, monthInt, yearInt, hourInt,
                                                                           minuteInt, 0, timezoneStr)
        dateTimeComponentSymbolList, separatorsList, dateTimeComponentValueList = DateTimeUtil.getFormattedDateTimeComponents(
            requestArrowDate, self.configurationMgr.dateTimeFormat)
        dateSeparator = separatorsList[0]
        timeSeparator = separatorsList[1]
        requestDateDMY = dateTimeComponentValueList[0] + dateSeparator + dateTimeComponentValueList[1] + dateSeparator + \
                         dateTimeComponentValueList[2]
        requestDateHM = dateTimeComponentValueList[3] + timeSeparator + dateTimeComponentValueList[4]

        from seqdiagbuilder import SeqDiagBuilder
        SeqDiagBuilder.recordFlow()

        return requestDateDMY, requestDateHM


    def toClipboard(self, numericVal):
        if os.name == 'posix':
            self._clipboard.copy(str(numericVal))
        else:
            if not self.activateClipboard:
                pass
            else:
                self._clipboard.copy(str(numericVal))


    def fromClipboard(self):
        if not self.activateClipboard:
            return 'Clipboard not available since not activated at ConsoleOutputFormater initialisation'
        else:
            return self._clipboard.paste()


if __name__ == '__main__':
    pr = GuiOutputFormater()
    y = round(5.59, 1)
    y = 0.999999999
    y = 0.9084
    y = 40
    yFormatted = '%.8f' % y
    print()
    print('No formatting:                 ' + str(y))
    print('With formatting:               ' + yFormatted)
    print('With formatting no trailing 0: ' + pr.formatFloatToStr(y))
    print()

    a = 12.56
    pr.toClipboard(a)
    print('Clipboard: ' + pr.fromClipboard())
