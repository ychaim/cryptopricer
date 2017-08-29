import re

ENTER_COMMAND_PROMPT = 'Enter command (h for help, q to quit)\n'

#pattern components constants
COMMAND_GRP_PATTERN = r"(\w+) \["
CURRENCY_SYMBOL_GRP_PATTERN = r"([A-Z]+)"
DD_MM_DATE_GRP_PATTERN = r"(\d+/\d+)"
HH_MM_TIME_GRP_PATTERN = r"(\d+:\d+)"
DOUBLE_PRICE_PATTERN = r"([0-9]+\.[0-9]+)"
DOUBLE_PRICE_PATTERN = r"(\d+\.\d+)"
EXCHANGE_SYMBOL_GRP_PATTERN = r"([A-Z]+)"


class Requester:
    '''
    Read in commands entered by the
    user, typically
    
    [btc 5/7 0.0015899 6/7 0.00153] [usd-chf] -nosave

    and return a dictionnary of commands
      
    {CRYPTO:[btc, 5/7, 0.0015899, 6/7, 0.00153], FIAT:[usd, chf], NOSAVE:[]}
    '''
    def __init__(self):
        self.commandQuit = None
        self.commandError = None
        self.commandCrypto = None
        self.commandTrade = None

    def request(self):
        inputStr = input(ENTER_COMMAND_PROMPT)
        upperInputStr = inputStr.upper()

        while upperInputStr == 'H':
            self._printHelp()
            inputStr = input(ENTER_COMMAND_PROMPT)
            upperInputStr = inputStr.upper()
        
        if upperInputStr == 'Q':
            return self.commandQuit
        else: #here, neither help nor quit demand entered. Need to determine which command
              #is entered by the user finding unique pattern match that identify this command
            userCommand = self._getUserCommand(inputStr, upperInputStr)

        if userCommand == self.commandError:
            return self.commandError

        if userCommand == "OO":
            upperInputStrWithoutUserCommand = upperInputStr[len(userCommand) + 1:]
            return self._parseCryptoCommandDataInput(inputStr, upperInputStrWithoutUserCommand)


    def _getUserCommand(self, inputStr, upperInputStr):
        match = re.match(COMMAND_GRP_PATTERN, upperInputStr)

        if match == None:
            self.commandError.rawParmData = inputStr
            self.commandError.parsedParmData = [self.commandError.USER_COMMAND_MISSING_MSG]
            return self.commandError

        return match.group(1)

    def _printHelp(self):
        print('Usage:\n')
        print('[btc 5/7 0.0015899 6/7 0.00153] [usd-chf]')
        print('Beware: IF YOU ENTER MORE THAN ONE FIAT CURRENCY, DO NOT FORGET TO SEPARATE THEM WITH A \'-\' !')
        inp = input('\nm for more or anything else to exit help\n')
        
        if inp.upper() == 'M':
            print("\n-ns or -nosave --> don't save retrieved prices")
            print("-rm [1, 3, 4] --> remove line numbers\n")

    def _parseCryptoCommandDataInput(self, inputStr, upperInputStrWithoutUserCommand):
        #convert [btc 5/7 0.0015899 6/7 0.00153] [usd-chf] -nosave
        #into
        #[CRYPTO:[btc, 5/7, 0.0015899, 6/7, 0.00153], FIAT:[usd, chf], NOSAVE:[]}
        cryptoDataList = self._parseCryptoDataFromInput(inputStr, upperInputStrWithoutUserCommand)

        if cryptoDataList == self.commandError:
            return self.commandError

        fiatDataList = self._parseFiatDataFromInput(upperInputStrWithoutUserCommand)

        self.commandCrypto.parsedParmData = [cryptoDataList, fiatDataList]

        return self.commandCrypto


    def _parseFiatDataFromInput(self, upperInputStrWithoutUserCommand):
        #convert [btc 5/7 0.0015899 6/7 0.00153] [usd-chf] -nosave
        #into
        #[usd, chf]
        
        fiatDataList = []
        patternFiat = r"(" + \
                      CURRENCY_SYMBOL_GRP_PATTERN + \
                      r"-)|(" + \
                      CURRENCY_SYMBOL_GRP_PATTERN + \
                      r"\])|(\[" + \
                      CURRENCY_SYMBOL_GRP_PATTERN + \
                      r"\])"

        for grp in re.finditer(patternFiat, upperInputStrWithoutUserCommand):
            for elem in grp.groups():
                if elem != None and len(elem) == 3:
                    fiatDataList.append(elem)

        return fiatDataList
        
    def _parseCryptoDataFromInput(self, inputStr, upperInputStrWithoutUserCommand):
        #convert [btc 5/7 0.0015899 6/7 0.00153] [usd-chf] -nosave
        #into
        #[btc, 5/7, 0.0015899, 6/7, 0.00153]
        
        cryptoDataList = []

        patternCryptoSymbol = r"\[" + \
                              CURRENCY_SYMBOL_GRP_PATTERN + \
                              " "
        
        match = re.match(patternCryptoSymbol, upperInputStrWithoutUserCommand)

        if match == None:
            self.commandError.rawParmData = inputStr
            self.commandError.parsedParmData = [self.commandError.CRYPTO_SYMBOL_MISSING_MSG]
            return self.commandError

        cryptoSymbol = match.group(1)

        cryptoDatePriceList = []
        patternDatePrice = DD_MM_DATE_GRP_PATTERN + \
                           r" " + \
                           DOUBLE_PRICE_PATTERN

        for grp in re.finditer(patternDatePrice, upperInputStrWithoutUserCommand):
            for elem in grp.groups():
                cryptoDatePriceList.append(elem)

        if len(cryptoDatePriceList) > 0:
            cryptoDataList.append(cryptoSymbol)
            cryptoDataList.extend(cryptoDatePriceList)
        else:
            return ''

        return cryptoDataList
                

if __name__ == '__main__':
    r = Requester()
    print(r._parseCryptoDataFromInput('[btc 5/7 0.0015899 6/7 0.00153] [usd-chf-eur] -nosave'))
