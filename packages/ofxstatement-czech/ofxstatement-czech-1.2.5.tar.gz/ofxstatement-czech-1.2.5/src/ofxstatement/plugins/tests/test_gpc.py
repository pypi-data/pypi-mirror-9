import glob
import logging
import os.path
import unittest

from ofxstatement.plugins.gpc import GPCParser


class TestParser(unittest.TestCase):
    pass


def test_generator(test_file_name):
    def test_parser(self):
        with open(test_file_name, 'rb') as test_file:
            parser = GPCParser(test_file)
            logging.debug('parser = dir {}'.format(dir(parser)))
            records = parser.split_records()
            self.assertGreater(len(list(records)), 0,
                               "split input into records\nrecords = %s"
                               % records)

    def test_parseLine(self):
        with open(test_file_name, 'rb') as test_file:
            parser = GPCParser(test_file)
            logging.debug('parser = dir {}'.format(dir(parser)))
            for rec_str in parser.split_records():
                rec = parser.parse_record(rec_str)
                if rec is None:
                    self.assertIsNotNone(parser.statement.start_balance)
                else:
                    self.assertIsNotNone(rec.id, "StatementLine NOT created")

    return test_parser, test_parseLine


def additional_tests():
    suite = unittest.TestSuite()
    test_samples_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "samples")
    tests = glob.glob(os.path.join(test_samples_dir, '*.gpc'))
    logging.debug('tests = {}'.format(tests))
    for t in tests:
        test_base = os.path.splitext(os.path.split(t)[1])[0]
        test_core = 'test_%s' % test_base
        tests = test_generator(t)
        for test in zip(['parser', 'parseLine'], tests):
            test_name = "{}_{}".format(test_core, test[0])
            setattr(TestParser, test_name, test[1])
            suite.addTest(TestParser(test_name))
    return suite

if __name__ == '__main__':
    unittest.main()
