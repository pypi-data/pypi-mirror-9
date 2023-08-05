"""Parser for the statement the Czech semi-formal standard GPC
(used by FIO, among others)"""
import logging
from decimal import Decimal

from ofxstatement.parser import StatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine

log = logging.getLogger('GPC')


class GPCParser(StatementParser):
    date_format = '%d%m%y'

    def __init__(self, inf, encoding="windows-1250", bank_id='2010'):
        super(GPCParser, self).__init__()
        log.debug('inf = {}'.format(inf))
        self.input = inf
        self.enc = encoding
        # Defaults to the bank_id of FIO banka, a.s.
        self.statement = Statement(bank_id=bank_id, currency='CZK')

    @staticmethod
    def get_acc_type(instr):
        if instr == ord('1'):
            return 'DEBIT'
        elif instr == ord('2'):
            return 'CREDIT'
        # OFX doesn't seem to be able to recognize storno transactions.
        #elif instr == ord('4'):
        #    return ACC_T.STORNO_DEBET
        #elif instr == ord('5'):
        #    return ACC_T.STORNO_KREDIT
        else:
            raise ValueError(
                'Unknown type of transation account: {}'.format(instr))

    @staticmethod
    def get_money(instr, signstr, pluschar='+'):
        instr = instr.decode().lstrip('0')
        if instr == '':
            instr = '0'
        num = Decimal(instr) / Decimal(100)
        if signstr == ord('-'):
            num = -num
        elif signstr != ord(pluschar):
            raise ValueError('Unknown sign "{}"'.format(signstr))
        return num

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        while True:
            res = self.input.read(130)
            if len(res) == 0:
                break
            yield res

    @staticmethod
    def __generate_statement_line(tr):
        memo_str = ''
        stat_line = StatementLine(id=tr['tr_statmt_no'],
                                  date=tr['maturity_date'],
                                  memo='',
                                  amount=tr['amount'])

        if len(tr['other_acc_no']) > 0:
            memo_str += 'For acc# {}'.format(tr['other_acc_no'])
        if len(tr['bank_code']) > 0:
            memo_str += '/{}'.format(tr['bank_code'])
        if len(tr['variable_symbol']) > 0:
            memo_str += ', VS: {}'.format(tr['variable_symbol'])
        if len(tr['specific_symbol']) > 0:
            memo_str += ', SS: {}'.format(tr['specific_symbol'])
        if len(tr['client_name']) > 0:
            memo_str += ', {}'.format(tr['client_name'])

        if len(memo_str) > 0:
            stat_line.memo = memo_str

        return stat_line

    def parse_record(self, line):
        """
        Each record is fixed-length (130 bytes) record type. There are
        two types of records distinguished by the first three bytes. If
        these are '074' then it is the whole statement record, if '075'
        then it is a transaction record.

        Statement record has this format:

            1-3     "074 " = type of record as "Data - výpis v Kč"
                    ("Data - statement in CZK")
            4-19    the account for which the statement is provided,
                    left-padded by zeros.
            20-39   20 alphanumeric characters of the shortened account name,
                    right-padded by spaces
            40-45   date of the previous statament in forma DDMMYY
            46-59   previous balance in hellers (1/100 CZK), 14 numeric
                    characters left-padded by zeros
            60      sign of previous balance, 1 character "+" or "-"
            61-74   current balance in hellers (1/100 CZK), 14 numeric
                    characters left-padded by zeros
            75      sign of the current balance, 1 character "+" or "-"
            76-89   amount of debet (MD) in hellers (1/100 CZK), 14
                    numeric characters left-padded by zeros
            90      sign of the debet amount (MD), 1 character "0" or "-"
            91-104  amount of kredit (D) in hellers (1/100 CZK), 14
                    numeric characters left-padded by zeros
            105     sign of the credit amount (D), 1 character "0" or "-"
            106-108 statement number
            109-114 statement date in format DDMMYY
            115-128 (filled by 14 spaces to make records of the same length)
            129-130 ending characters CR and LF

        Transaction record has this format:

            1-3     "075 " = type of record as "Data - obratová položka"
                    ("Data - transaction record")
            4-19    assigned account number 16 numeric characters
                    left-padded by zeros
            20–35   account number 16 numeric characters s vodící minulami
                    (or possibly prefix + account number)
            36–48   number of the transaction statement, 13 numeric characters
            49–60   amount in hellers (1/100 CZK) 12 numeric characters
                    left-padded by zeros
            61      accounting code in relation to the account number:
                    1 = debit transaction
                    2 = credit transaction
                    4 = storno of the debit transaction
                    5 = storno of the credit transaction
            62–71   variabile symbol 10 numeric characters left-padded by zeros
            72–81   constant symbol 10 numeric characters left-padded by
                    zeros in form BBBBKSYM, where:
                    BBBB = bank code
                    KSYM = constant symbol
            82–91   specific symbol 10 numeric characters left-padded by zeros
            92–97   "000000" = valuta
            98–117  20 alphanumeric characters shortened client name,
                    if necessary right-padded by spaces
            118     "0"
            119-122 "0203" = currency code for CZK
            123-128 maturity date in format DDMMYY
            129-130 ending characters CR and LF


        """
        assert len(line) == 130
        log.debug('line = {}'.format(line))

        act = {}
        trans = []
        typ = line[0:3]
        if typ == b'074':
            act['acc_no'] = line[3:19].decode().lstrip('0')
            act['acc_name'] = line[19:39].decode(self.enc).rstrip()
            act['orig_date'] = self.parse_datetime(line[39:45].decode())
            act['orig_amount'] = self.get_money(line[45:59], line[59])
            act['new_amount'] = self.get_money(line[60:74], line[74])
            act['debet_amount'] = self.get_money(line[75:89], line[89], '0')
            act['kredit_amount'] = self.get_money(line[90:104], line[104], '0')
            act['statement_no'] = int(line[105:108])
            act['statement_date'] = self.parse_datetime(line[108:114].decode())
        elif typ == b'075':
            tr = {}

            tr['acc_no'] = line[3:19].decode().lstrip('0')
            tr['other_acc_no'] = line[19:35].decode().lstrip('0')
            tr['tr_statmt_no'] = line[35:48].decode().lstrip('0')
            tr['amount'] = self.get_money(line[48:60], ord('+'))
            tr['other_acc_type'] = self.get_acc_type(line[60])
            tr['variable_symbol'] = line[61:71].decode().lstrip('0')
            var_s_bank_code = line[71:81].decode().lstrip('0')
            tr['bank_code'] = var_s_bank_code[0:4]
            tr['constant_symbol'] = var_s_bank_code[4:8]
            tr['specific_symbol'] = line[81:91].decode().lstrip('0')
            tr['client_name'] = line[97:117].decode(self.enc).rstrip()
            tr['maturity_date'] = self.parse_datetime(line[122:128].decode())

            if tr['other_acc_type'] in ('DEBIT'):  # TODO also STORNO_KREDIT
                tr['amount'] = -tr['amount']
            trans.append(tr)
        else:
            raise ValueError('Unknown type of account {}'.format(typ.decode()))

        if act:
            self.statement.start_balance = act['orig_amount']
            self.statement.start_date = act['orig_date']

            self.statement.end_balance = act['new_amount']
            self.statement.end_date = act['statement_date']
        else:
            return self.__generate_statement_line(tr)


class GPCPlugin(Plugin):
    def get_parser(self, fin):
        encoding = self.settings.get('charset', 'windows-1250')
        inf = open(fin, 'rb')
        return GPCParser(inf, encoding=encoding)
