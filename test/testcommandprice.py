import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import re
from datetimeutil import DateTimeUtil
from configurationmanager import ConfigurationManager
from pricerequester import PriceRequester
from crypcompexchanges import CrypCompExchanges
from processor import Processor
from commandprice import  CommandPrice


class TestCommandPrice(unittest.TestCase):
    def setUp(self):
        if os.name == 'posix':
            FILE_PATH = '/sdcard/cryptopricer.ini'
        else:
            FILE_PATH = 'c:\\temp\\cryptopricer.ini'

        self.configMgr = ConfigurationManager(FILE_PATH)
        self.priceRequester = PriceRequester()
        self.crypCompExchanges = CrypCompExchanges()
        self.processor = Processor(self.configMgr, self.priceRequester, self.crypCompExchanges)
        self.commandPrice = CommandPrice(self.processor, self.configMgr)


    def testExecuteHistoricalPriceFourDigitYear(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '12'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '9'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '2017'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), 'BTC')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), 'USD')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), 'BitTrex')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), resultData.PRICE_TYPE_HISTO_DAY)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE), 4122)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), '12/09/17 00:00')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TIME_STAMP), 1505174400)


    def testExecuteHistoricalPriceTwoDigitYear(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '12'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '9'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), 'BTC')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), 'USD')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), 'BitTrex')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), resultData.PRICE_TYPE_HISTO_DAY)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE), 4122)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), '12/09/17 00:00')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TIME_STAMP), 1505174400)


    def testExecuteHistoricalPriceNoYear(self):
        testDayStr = '1'
        testMonthStr = '1'
        testHourStr = '01'
        testMinuteStr = '15'
        testTimeZoneStr = 'Europe/Zurich'

        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = testDayStr
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = testMonthStr
        #self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '2017'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = testHourStr
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = testMinuteStr

        resultData = self.commandPrice.execute()

        now = DateTimeUtil.localNow(testTimeZoneStr)
        fourDigitYear = now.year
        nowYear = fourDigitYear - 2000
        nowYearStr = str(nowYear)

        testDateTime = DateTimeUtil.dateTimeComponentsToArrowLocalDate(int(testDayStr), int(testMonthStr), fourDigitYear, int(testHourStr), int(testMinuteStr), 0, testTimeZoneStr)

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), 'BTC')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), 'USD')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), 'BitTrex')

        if DateTimeUtil.isDateOlderThan(testDateTime, 7):
            self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), resultData.PRICE_TYPE_HISTO_DAY)
            self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), '01/01/{} 00:00'.format(nowYearStr))
        else:
            self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), resultData.PRICE_TYPE_HISTO_MINUTE)
            self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), '01/01/{} {}:{}'.format(nowYearStr, testHourStr, testMinuteStr))


    def testExecuteHistoricalPriceNoMonth(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = None
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = None
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        now = DateTimeUtil.localNow('Europe/Zurich')

        nowMonth = now.month

        if nowMonth < 10:
            nowMonthStr = '0' + str(nowMonth)
        else:
            nowMonthStr = str(nowMonth)

        nowYear = now.year - 2000

        nowYearStr = str(nowYear)

        self.assertIsNone(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG))


    def testExecuteHistoricalPriceWrongExchange(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'Unknown'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '12'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '9'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '2017'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG), "ERROR - Unknown market does not exist for this coin pair (BTC-USD)")
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TIME_STAMP), None)


    def removePriceFromResult(self, resultStr):
        match = re.match(r"(.*) ([\d\.]*)", resultStr)

        if match != None:
            return match.group(1)
        else:
            return ()


    def testExecuteRealTimePrice(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '0'

        resultData = self.commandPrice.execute()

        now, nowDayStr, nowMonthStr, nowHourStr, nowMinuteStr = self.getFormattedNowDateTimeComponents()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), 'BTC')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), 'USD')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), 'BitTrex')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), resultData.PRICE_TYPE_RT)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), '{}/{}/{} {}:{}'.format(nowDayStr, nowMonthStr, now.year - 2000, nowHourStr, nowMinuteStr))

    def getFormattedNowDateTimeComponents(self):
        now = DateTimeUtil.localNow('Europe/Zurich')
        nowMinute = now.minute
        if nowMinute < 10:
            if nowMinute > 0:
                nowMinuteStr = '0' + str(nowMinute)
            else:
                nowMinuteStr = '00'
        else:
            nowMinuteStr = str(nowMinute)
        nowHour = now.hour
        if nowHour < 10:
            if nowHour > 0:
                nowHourStr = '0' + str(nowHour)
            else:
                nowHourStr = '00'
        else:
            nowHourStr = str(nowHour)
        nowDay = now.day
        if nowDay < 10:
            nowDayStr = '0' + str(nowDay)
        else:
            nowDayStr = str(nowDay)
        nowMonth = now.month
        if nowMonth < 10:
            nowMonthStr = '0' + str(nowMonth)
        else:
            nowMonthStr = str(nowMonth)
        return now, nowDayStr, nowMonthStr, nowHourStr, nowMinuteStr

    def testExecuteRealTimePriceWrongExchange(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'Unknown'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()


        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - Unknown market does not exist for this coin pair (BTC-USD)")
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), None)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TIME_STAMP), None)


    def testExecuteRealTimePriceInvalidYearOneDigit(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - date not valid")


    def testExecuteHistoDayPriceInvalidYearIsZero(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '0'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - date not valid")


    def testExecuteRealTimePriceInvalidYearThreeDigit(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '017'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - 017 not conform to accepted year format (YYYY, YY or '')")


    def testExecuteRealTimePriceInvalidYearFiveDigit(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '20017'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - 20017 not conform to accepted year format (YYYY, YY or '')")


    def testExecuteRealTimePriceInvalidMonthThreeDigit(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '21'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '112'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - 112 not conform to accepted month format (MM or M)")


    def testExecuteRealTimePriceInvalidDayThreeDigit(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '211'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '11'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - day is out of range for month")


    def testExecuteRealTimePriceInvalidDayValue(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '32'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '11'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = None

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - day is out of range for month")


    def testExecuteRealTimePriceInvalidMonthValue(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '31'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '13'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = None
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - month must be in 1..12")


    def testExecuteRealTimePriceInvalidHourValue(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '31'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '12'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '25'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - hour must be in 0..23")


    def testExecuteRealTimePriceInvalidMinuteValue(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '31'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '12'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '65'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - minute must be in 0..59")


    def testExecuteHistoricalPriceDateOneYearFromNow(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'

        now, nowDayStr, nowMonthStr, nowHourStr, nowMinuteStr = self.getFormattedNowDateTimeComponents()

        self.commandPrice.parsedParmData[self.commandPrice.DAY] = nowDayStr
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = nowMonthStr
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = str(now.year + 1)
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = nowHourStr
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = nowMinuteStr

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG), None)
        self.assertTrue(resultData.containsWarning(resultData.WARNING_TYPE_FUTURE_DATE))
        self.assertEqual(resultData.getWarningMessage(resultData.WARNING_TYPE_FUTURE_DATE), "Warning - request date {}/{}/{} {}:{} can not be in the future and was shifted back to last year".format(nowDayStr, nowMonthStr, (now.year + 1 - 2000), nowHourStr, nowMinuteStr))
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), 'BTC')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), 'USD')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), 'BitTrex')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), resultData.PRICE_TYPE_HISTO_DAY)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), "{}/{}/{} 00:00".format(nowDayStr, nowMonthStr, (now.year - 1) - 2000))


    def testExecuteHistoricalPriceDateTwoYearsFromNowNoTime(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'

        now, nowDayStr, nowMonthStr, nowHourStr, nowMinuteStr = self.getFormattedNowDateTimeComponents()

        self.commandPrice.parsedParmData[self.commandPrice.DAY] = nowDayStr
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = nowMonthStr
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = str(now.year + 2)
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = None
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = None

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG), None)
        self.assertTrue(resultData.containsWarning(resultData.WARNING_TYPE_FUTURE_DATE))
        self.assertEqual(resultData.getWarningMessage(resultData.WARNING_TYPE_FUTURE_DATE), "Warning - request date {}/{}/{} 00:00 can not be in the future and was shifted back to last year".format(nowDayStr, nowMonthStr, (now.year + 2 - 2000)))
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), 'BTC')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), 'USD')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), 'BitTrex')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), resultData.PRICE_TYPE_HISTO_DAY)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), "{}/{}/{} 00:00".format(nowDayStr, nowMonthStr, (now.year - 1) - 2000))


    def testExecuteHistoricalPriceDateOneMinuteFromNow(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'

        now, nowDayStr, nowMonthStr, nowHourStr, nowMinuteStr = self.getFormattedNowDateTimeComponents()

        minutePlusOne = (now.minute + 1) % 60

        if minutePlusOne < 10:
            if minutePlusOne > 0:
                nowMinutePlusOneStr = '0' + str(minutePlusOne)
            else:
                nowMinutePlusOneStr = '00'
        else:
            nowMinutePlusOneStr = str(minutePlusOne)

        self.commandPrice.parsedParmData[self.commandPrice.DAY] = nowDayStr
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = nowMonthStr
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = str(now.year)
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = nowHourStr
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = nowMinutePlusOneStr

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG), None)
        self.assertTrue(resultData.containsWarning(resultData.WARNING_TYPE_FUTURE_DATE))
        self.assertEqual(resultData.getWarningMessage(resultData.WARNING_TYPE_FUTURE_DATE), "Warning - request date {}/{}/{} {}:{} can not be in the future and was shifted back to last year".format(nowDayStr, nowMonthStr, (now.year - 2000), nowHourStr, nowMinutePlusOneStr))
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_CRYPTO), 'BTC')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_FIAT), 'USD')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_EXCHANGE), 'BitTrex')
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_TYPE), resultData.PRICE_TYPE_HISTO_DAY)
        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_PRICE_DATE_TIME_STRING), "{}/{}/{} 00:00".format(nowDayStr, nowMonthStr, (now.year - 1 - 2000)))


    def testExecuteRealTimePriceInvalidYearNonDigit(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = 'O7'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - invalid value: O7 violates format for year (DD/MM/YY)")


    def testExecuteRealTimePriceInvalidDayFormat(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '10:00'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - invalid value: invalid value 10:00 violates format for day (DD/MM)")


    def testExecuteRealTimePriceInvalidDayFormat(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = 'o1'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - invalid value: o1 violates format for month (DD/MM)")


    def testExecuteRealTimePriceInvalidHourFormat(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '1o'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = '5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - invalid value: 1o violates format for hour (HH:mm)")


    def testExecuteRealTimePriceInvalidMinuteFormat(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = 'o5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - invalid value: o5 violates format for minute (HH:mm)")


    def testExecuteRealTimePriceInvalidFiat(self):
        self.commandPrice.parsedParmData[self.commandPrice.CRYPTO] = 'btc'
        self.commandPrice.parsedParmData[self.commandPrice.FIAT] = 'usd6'
        self.commandPrice.parsedParmData[self.commandPrice.EXCHANGE] = 'bittrex'
        self.commandPrice.parsedParmData[self.commandPrice.DAY] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MONTH] = '1'
        self.commandPrice.parsedParmData[self.commandPrice.YEAR] = '17'
        self.commandPrice.parsedParmData[self.commandPrice.HOUR] = '10'
        self.commandPrice.parsedParmData[self.commandPrice.MINUTE] = 'o5'

        resultData = self.commandPrice.execute()

        self.assertEqual(resultData.getValue(resultData.RESULT_KEY_ERROR_MSG),
                         "ERROR - fiat missing or invalid")


if __name__ == '__main__':
    unittest.main()
