import unittest
from hypothesis import given
from hypothesis.descriptors import one_of, SampledFrom, Just, sampled_from, just
from hypothesis.searchstrategy import MappedSearchStrategy, StringStrategy
from hypothesis.strategytable import StrategyTable
from segpy.encoding import EBCDIC, ASCII
from segpy.toolkit import format_extended_textual_header, CARDS_PER_HEADER, END_TEXT_STANZA, CARD_LENGTH
from segpy.portability import unicode


class MultiLineString(unicode):
    pass


class MultiLineStringStrategy(MappedSearchStrategy):

    def pack(self, x):
        return MultiLineString(unicode('\n').join(x))

    def unpack(self, x):
        return x.splitlines()


StrategyTable.default().define_specification_for(
    MultiLineString,
    lambda s, d: MultiLineStringStrategy(
        strategy=s.strategy([unicode]),
        descriptor=MultiLineString))


class TestFormatExtendedTextualHeader(unittest.TestCase):

    @given(MultiLineString,
           sampled_from([ASCII, EBCDIC]),
           bool)
    def test_forty_lines_per_page(self, text, encoding, include_text_stop):
        pages = format_extended_textual_header(text, encoding, include_text_stop)
        self.assertTrue(all(len(page) == CARDS_PER_HEADER for page in pages))

    @given(MultiLineString,
           sampled_from([ASCII, EBCDIC]),
           bool)
    def test_eighty_bytes_per_encoded_line(self, text, encoding, include_text_stop):
        pages = format_extended_textual_header(text, encoding, include_text_stop)
        self.assertTrue(all([len(line.encode(encoding)) == CARD_LENGTH for page in pages for line in page]))

    @given(MultiLineString,
           sampled_from([ASCII, EBCDIC]),
           bool)
    def test_lines_end_with_cr_lf(self, text, encoding, include_text_stop):
        pages = format_extended_textual_header(text, encoding, include_text_stop)
        self.assertTrue(all([line.endswith('\r\n') for page in pages for line in page]))

    @given(MultiLineString,
           sampled_from([ASCII, EBCDIC]),
           just(True))
    def test_end_text_stanza_present(self, text, encoding, include_text_stop):
        pages = format_extended_textual_header(text, encoding, include_text_stop)
        self.assertTrue(pages[-1][0].startswith(END_TEXT_STANZA))


if __name__ == '__main__':
    unittest.main()