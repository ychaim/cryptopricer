import unittest
import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from commanderror import CommandError
from priceresult import PriceResult

class TestCommandError(unittest.TestCase):

    def testCommandErrorInstanciation(self):
        commandError = CommandError(None)
        commandError.rawParmData = "-c"
        commandError.parsedParmData = [commandError.CRYPTO_SYMBOL_MISSING_MSG]


        priceResult = commandError.execute()
        self.assertEqual("ERROR - invalid command -c: crypto symbol missing", priceResult.getValue(PriceResult.RESULT_KEY_ERROR_MSG))


if __name__ == '__main__':
    unittest.main()