import unittest
import glob
import os.path
from ofxstatement.plugins.maxibps import PSTextFormatParser


class TestParser(unittest.TestCase):
    pass


def test_generator(test_file_name):
    def test_parser(self):
        with open(test_file_name, "U", encoding="utf-8-sig") as test_file:
            parser = PSTextFormatParser(test_file)
            records = parser.split_records()
            self.assertGreater(len(records), 0,
                               "split input into records\nrecords = %s"
                               % records)

    def test_parseLine(self):
        with open(test_file_name, "U", encoding="utf-8-sig") as test_file:
            parser = PSTextFormatParser(test_file)
            for rec_str in parser.split_records():
                rec = parser.parse_record(rec_str)
                self.assertIsNotNone(rec, "StatementLine created")

    return test_parser, test_parseLine


def additional_tests():
    suite = unittest.TestSuite()
    test_samples_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "samples")
    tests = glob.glob(os.path.join(test_samples_dir, '*.txt'))
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
