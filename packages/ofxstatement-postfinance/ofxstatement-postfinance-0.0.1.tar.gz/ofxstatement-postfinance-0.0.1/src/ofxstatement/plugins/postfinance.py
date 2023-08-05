from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import StatementLine
import csv
import decimal
import re

from ofxstatement.parser import CsvStatementParser
import csv
from io import StringIO

BANKSIGNATURES = (
"Date\tPosting details\tCredit\tDebit\tValue\tBalance"
)

CREDITSIGNATURES = (
"Date\tBilling month\tDescription\tCredit\tDebit\tTotal"
)

payeesplit = False

payeefinder = [
        re.compile("SALES.SERVICE DATED \d+.\d+.\d+ CARD NO. ?X+\d+ (.*)"),
        re.compile("E-FINANCE \d+-\d+-\d+ (.*)"),

        re.compile("GIRO INTERNATIONAL \w+ \d+.\d+ EXCHANGE RATE \d+.\d+ (.*)"),
        re.compile("GIRO FROM .+ MAILER: (.*)"),
        re.compile("GIRO FROM ACCOUNT (.*)"),
        
        # Cash withdrawals includes card no to see what card was used 
        re.compile("CASH WITHDRAWAL DATED \S+ CARD NO. (.*)"), 
        re.compile("CASH WITHDRAWAL ON \S+ CARD NO. (.*)"), 
        re.compile("WITHDRAWAL OF \d+.\d+.\d+ \S+ \S+ AT EXCHANGE RATE \S+ CARD NO. (.*)"),
        
        re.compile("DEBIT DIRECT ORDER CUSTOMER NUMBER (.*)"),
        re.compile("OTHER: (.*)"),
        re.compile("GIRO INTERNATIONAL \(SEPA\) \S+ \S+ EXCHANGE RATE \d+.\d+ (.*)"),
        re.compile("TRANSFER POSTFINANCE MOBILE FAST SERVICE : (.*)"),

        re.compile("PURCHASE/ONLINE SHOPPING OF \S+ CARD NO. (.*)"),
        
        ## The following are those that dont have a clear payee so need it all to know what is is
        re.compile("(LOAD CREDIT CARD ACCOUNT .*)"), # no unique id so leaving it as is.
        re.compile("(E-FINANCE ACCOUNT: .*)"), # keep all
        re.compile("(INTEREST STATEMENT .*)")
        
        ]

                
                
class PostFinanceBankParser(CsvStatementParser):

    mappings = { "date": 0, "memo": 1}
    date_format = "%Y%m%d"

    def split_records(self):
        #print("split records")
        return csv.reader(self.fin, delimiter='\t', quotechar='"')

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """
        #print(line)
        sl = StatementLine()
        sl = super(PostFinanceBankParser,self).parse_record(line)

        if not line[3]:
            sl.amount = self.parse_float(line[2])
            sl.trntype='CREDIT'
        else:
            sl.amount = self.parse_float("-" + line[3])
            sl.trntype='DEBIT'

        sl.payee = sl.memo

        if payeesplit: #TODO: enable via settings
            found = False
            for regex in payeefinder:
                m = regex.match(sl.payee)
                if m:
                    found = True
                    sl.payee = m.group(1)

                 #if not found:
                 #   print ("Found No PAYEE!" + sl.memo)
        
        return sl

class PostFinanceCreditParser(CsvStatementParser):

    mappings = { "date": 0, "memo": 2}
    date_format = "%Y%m%d"

    def split_records(self):
        result = []

        datepattern = re.compile("^\d\d\d\d\d\d\d\d\t")

        previousline = None
        
        for line in self.fin:
            line = line.rstrip()
            if(datepattern.match(line)):
                if previousline:
                    result.append(previousline)
                    previousline = None
                previousline = line
            else:
                if previousline:
                    previousline += " " + line
                else:
                    previousline = line

        if previousline:
            result.append(previousline)
            
        return csv.reader(result, delimiter='\t', quotechar='"')

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """
        #print(line)
        sl = StatementLine()
        sl = super(PostFinanceCreditParser,self).parse_record(line)

        #print(line)
        if not line[3]:
            sl.amount = self.parse_float(line[4])
            sl.trntype='CREDIT'
        else:
            sl.amount = self.parse_float("-" + line[3])
            sl.trntype='DEBIT'

        sl.payee = sl.memo
        
        return sl

class PostFinanceBank(Plugin):
    """PostFinance Bank .tab format
    """

    def get_csv_signature(self, csvfile):
        #print("get_csv_signature")
        return csvfile.readline().strip()
    
    def get_parser(self, fin):
        #print("get_parser")
        f = open(fin, "r", encoding="latin1")
        signature = self.get_csv_signature(f)
        if signature in BANKSIGNATURES:
            parser = PostFinanceBankParser(f)
            parser.statement.account_id = self.settings.get('account','default')
            parser.statement.currency = self.settings.get('currency', 'CHF')
            parser.statement.bank_id =  self.settings.get('bank', 'PostFinance')
            return parser
        elif signature in CREDITSIGNATURES:
            parser = PostFinanceCreditParser(f)
            parser.statement.account_id = self.settings.get('card','creditcard')
            parser.statement.currency = self.settings.get('currency', 'CHF')
            parser.statement.bank_id =  self.settings.get('bank', 'PostFinance')
            return parser
            
        
        # no plugin with matching signature was found
        f.close()
        raise Exception(signature + " does not match")
