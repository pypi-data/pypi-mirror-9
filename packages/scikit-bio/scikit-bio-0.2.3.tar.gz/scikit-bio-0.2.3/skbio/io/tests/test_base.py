# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function
from future.builtins import range, zip

import unittest

import numpy.testing as npt

from skbio import BiologicalSequence, DNASequence, RNASequence
from skbio.io._base import (_chunk_str, _decode_qual_to_phred,
                            _encode_phred_to_qual, _get_nth_sequence,
                            _parse_fasta_like_header,
                            _format_fasta_like_records)


class ChunkStrTests(unittest.TestCase):
    def test_even_split(self):
        self.assertEqual(_chunk_str('abcdef', 6, ' '), 'abcdef')
        self.assertEqual(_chunk_str('abcdef', 3, ' '), 'abc def')
        self.assertEqual(_chunk_str('abcdef', 2, ' '), 'ab cd ef')
        self.assertEqual(_chunk_str('abcdef', 1, ' '), 'a b c d e f')
        self.assertEqual(_chunk_str('a', 1, ' '), 'a')
        self.assertEqual(_chunk_str('abcdef', 2, ''), 'abcdef')

    def test_no_split(self):
        self.assertEqual(_chunk_str('', 2, '\n'), '')
        self.assertEqual(_chunk_str('a', 100, '\n'), 'a')
        self.assertEqual(_chunk_str('abcdef', 42, '|'), 'abcdef')

    def test_uneven_split(self):
        self.assertEqual(_chunk_str('abcdef', 5, '|'), 'abcde|f')
        self.assertEqual(_chunk_str('abcdef', 4, '|'), 'abcd|ef')
        self.assertEqual(_chunk_str('abcdefg', 3, ' - '), 'abc - def - g')

    def test_invalid_n(self):
        with self.assertRaisesRegexp(ValueError, 'n=0'):
            _chunk_str('abcdef', 0, ' ')

        with self.assertRaisesRegexp(ValueError, 'n=-42'):
            _chunk_str('abcdef', -42, ' ')


class PhredDecoderTests(unittest.TestCase):
    def test_missing_variant_and_phred_offset(self):
        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred('abcd')
        self.assertIn('`variant`', str(cm.exception))
        self.assertIn('`phred_offset`', str(cm.exception))
        self.assertIn('decode', str(cm.exception))

    def test_variant_and_phred_offset_provided(self):
        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred('abcd', variant='sanger', phred_offset=64)
        self.assertIn('both', str(cm.exception))
        self.assertIn('`variant`', str(cm.exception))
        self.assertIn('`phred_offset`', str(cm.exception))

    def test_solexa_variant(self):
        with self.assertRaises(NotImplementedError) as cm:
            _decode_qual_to_phred('abcd', variant='solexa')
        self.assertIn('719', str(cm.exception))

    def test_unrecognized_variant(self):
        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred('abcd', variant='illumina')
        self.assertIn('variant', str(cm.exception))
        self.assertIn("'illumina'", str(cm.exception))

    def test_empty_qual_str(self):
        self.assertEqual(_decode_qual_to_phred('', variant='sanger'), [])

    def test_sanger_variant(self):
        # test entire range of possible ascii chars for sanger
        all_sanger_ascii = ('!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOP'
                            'QRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
        obs = _decode_qual_to_phred(all_sanger_ascii, variant='sanger')
        self.assertEqual(obs, list(range(94)))

        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred('a b', variant='sanger')
        self.assertIn('-1', str(cm.exception))
        self.assertIn('[0, 93]', str(cm.exception))

    def test_illumina13_variant(self):
        # test entire range of possible ascii chars for illumina1.3
        all_illumina13_ascii = ('@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijk'
                                'lmnopqrstuvwxyz{|}~')
        obs = _decode_qual_to_phred(all_illumina13_ascii,
                                    variant='illumina1.3')
        self.assertEqual(obs, list(range(63)))

        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred('a!b', variant='illumina1.3')
        self.assertIn('-31', str(cm.exception))
        self.assertIn('[0, 62]', str(cm.exception))

    def test_illumina18_variant(self):
        # test entire range of possible ascii chars for illumina1.8
        all_illumina18_ascii = ('!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKL'
                                'MNOPQRSTUVWXYZ[\\]^_')
        obs = _decode_qual_to_phred(all_illumina18_ascii,
                                    variant='illumina1.8')
        self.assertEqual(obs, list(range(63)))

        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred('AaB', variant='illumina1.8')
        self.assertIn('64', str(cm.exception))
        self.assertIn('[0, 62]', str(cm.exception))

    def test_custom_phred_offset(self):
        ascii_chars = '*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\'
        obs = _decode_qual_to_phred(ascii_chars, phred_offset=42)
        self.assertEqual(obs, list(range(51)))

        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred(ascii_chars, phred_offset=43)
        self.assertIn('-1', str(cm.exception))
        self.assertIn('[0, 83]', str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred(ascii_chars, phred_offset=0)
        self.assertIn('`phred_offset`', str(cm.exception))
        self.assertIn('0', str(cm.exception))
        self.assertIn('printable', str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            _decode_qual_to_phred(ascii_chars, phred_offset=127)
        self.assertIn('`phred_offset`', str(cm.exception))
        self.assertIn('127', str(cm.exception))
        self.assertIn('printable', str(cm.exception))


class PhredEncoderTests(unittest.TestCase):
    def test_missing_variant_and_phred_offset(self):
        with self.assertRaises(ValueError) as cm:
            _encode_phred_to_qual([1, 2, 3])
        self.assertIn('`variant`', str(cm.exception))
        self.assertIn('`phred_offset`', str(cm.exception))
        self.assertIn('encode', str(cm.exception))

    def test_variant_and_phred_offset_provided(self):
        with self.assertRaises(ValueError) as cm:
            _encode_phred_to_qual([1, 2, 3], variant='sanger', phred_offset=64)
        self.assertIn('both', str(cm.exception))
        self.assertIn('`variant`', str(cm.exception))
        self.assertIn('`phred_offset`', str(cm.exception))

    def test_solexa_variant(self):
        with self.assertRaises(NotImplementedError) as cm:
            _encode_phred_to_qual([1, 2, 3], variant='solexa')
        self.assertIn('719', str(cm.exception))

    def test_unrecognized_variant(self):
        with self.assertRaises(ValueError) as cm:
            _encode_phred_to_qual([1, 2, 3], variant='illumina')
        self.assertIn('variant', str(cm.exception))
        self.assertIn("'illumina'", str(cm.exception))

    def test_no_phred_scores(self):
        self.assertEqual(_encode_phred_to_qual([], variant='sanger'), '')

    def test_sanger_variant(self):
        # test entire range of possible ascii chars for sanger
        all_sanger_ascii = ('!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOP'
                            'QRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
        obs = _encode_phred_to_qual(list(range(94)), variant='sanger')
        self.assertEqual(obs, all_sanger_ascii)

        with self.assertRaises(ValueError) as cm:
            _encode_phred_to_qual([42, -1, 33], variant='sanger')
        self.assertIn('-1', str(cm.exception))
        self.assertIn('[0, 93]', str(cm.exception))

        obs = npt.assert_warns(UserWarning, _encode_phred_to_qual,
                               [42, 94, 33], variant='sanger')
        self.assertEqual(obs, 'K~B')

    def test_illumina13_variant(self):
        # test entire range of possible ascii chars for illumina1.3
        all_illumina13_ascii = ('@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijk'
                                'lmnopqrstuvwxyz{|}~')
        obs = _encode_phred_to_qual(list(range(63)), variant='illumina1.3')
        self.assertEqual(obs, all_illumina13_ascii)

        with self.assertRaises(ValueError) as cm:
            _encode_phred_to_qual([42, -1, 33], variant='illumina1.3')
        self.assertIn('-1', str(cm.exception))
        self.assertIn('[0, 62]', str(cm.exception))

        obs = npt.assert_warns(UserWarning, _encode_phred_to_qual,
                               [42, 63, 33], variant='illumina1.3')
        self.assertEqual(obs, 'j~a')

    def test_illumina18_variant(self):
        # test entire range of possible ascii chars for illumina1.8
        all_illumina18_ascii = ('!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKL'
                                'MNOPQRSTUVWXYZ[\\]^_')
        obs = _encode_phred_to_qual(list(range(63)), variant='illumina1.8')
        self.assertEqual(obs, all_illumina18_ascii)

        with self.assertRaises(ValueError) as cm:
            _encode_phred_to_qual([42, -1, 33], variant='illumina1.8')
        self.assertIn('-1', str(cm.exception))
        self.assertIn('[0, 62]', str(cm.exception))

        obs = npt.assert_warns(UserWarning, _encode_phred_to_qual,
                               [42, 63, 33], variant='illumina1.8')
        self.assertEqual(obs, 'K_B')

    def test_custom_phred_offset(self):
        ascii_chars = '*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\'
        obs = _encode_phred_to_qual(list(range(51)), phred_offset=42)
        self.assertEqual(obs, ascii_chars)

        with self.assertRaises(ValueError) as cm:
            _encode_phred_to_qual([42, -1, 33], phred_offset=42)
        self.assertIn('-1', str(cm.exception))
        self.assertIn('[0, 84]', str(cm.exception))

        obs = npt.assert_warns(UserWarning, _encode_phred_to_qual,
                               [42, 255, 33], phred_offset=42)
        self.assertEqual(obs, 'T~K')


class TestGetNthSequence(unittest.TestCase):
    def setUp(self):
        def generator():
            for i in range(1, 6):
                yield 'goldilocks: ' + str(i)

        self.gen = generator()

    def test_seq_num_too_small(self):
        with self.assertRaises(ValueError) as cm:
            _get_nth_sequence(self.gen, 0)

        self.assertIn('between 1 and', str(cm.exception))
        self.assertIn('0', str(cm.exception))

    def test_seq_num_too_big(self):
        with self.assertRaises(ValueError) as cm:
            _get_nth_sequence(self.gen, 6)

        self.assertIn('end of file', str(cm.exception))
        self.assertIn('6th', str(cm.exception))

    def test_seq_num_just_right(self):
        value = _get_nth_sequence(self.gen, 3)
        self.assertEqual(value, 'goldilocks: 3')


class TestParseFASTALikeHeader(unittest.TestCase):
    def test_no_id_or_description(self):
        obs = _parse_fasta_like_header('> \t\t  \n')
        self.assertEqual(obs, ('', ''))

    def test_id_only(self):
        obs = _parse_fasta_like_header('>suht! \t\t  \n')
        self.assertEqual(obs, ('suht!', ''))

    def test_description_only(self):
        obs = _parse_fasta_like_header('> suht! \t\t  \n')
        self.assertEqual(obs, ('', 'suht!'))

    def test_id_and_description(self):
        obs = _parse_fasta_like_header('>!thus  suht! \t\t  \n')
        self.assertEqual(obs, ('!thus', 'suht!'))


class TestFormatFASTALikeRecords(unittest.TestCase):
    def setUp(self):
        def generator():
            yield BiologicalSequence('ACGT', id='', description='',
                                     quality=range(4))
            yield RNASequence('GAU', id='  foo \t\t bar ', description='')
            yield DNASequence('TAG', id='', description='foo\n\n bar\n')
            yield BiologicalSequence('A', id='foo', description='bar baz',
                                     quality=[42])
        self.gen = generator()

    def test_no_replacement(self):
        exp = [
            ('', 'ACGT', range(4)),
            ('  foo \t\t bar ', 'GAU', None),
            (' foo\n\n bar\n', 'TAG', None),
            ('foo bar baz', 'A', [42])
        ]
        obs = list(_format_fasta_like_records(self.gen, None, None, False))

        self.assertEqual(len(obs), len(exp))
        for o, e in zip(obs, exp):
            npt.assert_equal(o, e)

    def test_empty_str_replacement(self):
        exp = [
            ('', 'ACGT', range(4)),
            ('foobar', 'GAU', None),
            (' foo bar', 'TAG', None),
            ('foo bar baz', 'A', [42])
        ]
        obs = list(_format_fasta_like_records(self.gen, '', '', False))

        self.assertEqual(len(obs), len(exp))
        for o, e in zip(obs, exp):
            npt.assert_equal(o, e)

    def test_multi_char_replacement(self):
        exp = [
            ('', 'ACGT', range(4)),
            ('-.--.-foo-.--.--.--.-bar-.-', 'GAU', None),
            (' foo_-__-_ bar_-_', 'TAG', None),
            ('foo bar baz', 'A', [42])
        ]
        obs = list(_format_fasta_like_records(self.gen, '-.-', '_-_', False))

        self.assertEqual(len(obs), len(exp))
        for o, e in zip(obs, exp):
            npt.assert_equal(o, e)

    def test_newline_character_in_id_whitespace_replacement(self):
        with self.assertRaisesRegexp(ValueError, 'Newline character'):
            list(_format_fasta_like_records(self.gen, '-\n--', ' ', False))

    def test_newline_character_in_description_newline_replacement(self):
        with self.assertRaisesRegexp(ValueError, 'Newline character'):
            list(_format_fasta_like_records(self.gen, None, 'a\nb', False))

    def test_empty_sequence(self):
        def blank_seq_gen():
            for seq in (DNASequence('A'), BiologicalSequence(''),
                        RNASequence('GG')):
                yield seq

        with self.assertRaisesRegexp(ValueError, '2nd.*empty'):
            list(_format_fasta_like_records(blank_seq_gen(), None, None,
                                            False))

    def test_missing_quality_scores(self):
        def missing_qual_gen():
            for seq in (RNASequence('A', quality=[42]),
                        BiologicalSequence('AG'),
                        DNASequence('GG', quality=[41, 40])):
                yield seq

        with self.assertRaisesRegexp(ValueError,
                                     '2nd sequence.*quality scores'):
            list(_format_fasta_like_records(missing_qual_gen(), '-', '-',
                                            True))


if __name__ == '__main__':
    unittest.main()
