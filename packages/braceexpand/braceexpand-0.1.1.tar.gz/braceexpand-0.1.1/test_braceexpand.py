import unittest
from braceexpand import braceexpand, UnbalancedBracesError

class BraceExpand(unittest.TestCase):
    tests = [
            ('{1,2}', ['1', '2']),
            ('{1}', ['{1}']),
            ('{1,2{}}', ['1', '2{}']),
            ('}{', ['}{']),
            ('a{b,c}d{e,f}', ['abde', 'abdf', 'acde', 'acdf']),
            ('a{b,c{d,e,}}', ['ab', 'acd', 'ace', 'ac']),
            ('a{b,{c,{d,e}}}', ['ab', 'ac', 'ad', 'ae']),
            ('{{a,b},{c,d}}', ['a', 'b', 'c', 'd']),
            ('{7..10}', ['7', '8', '9', '10']),
            ('{10..7}', ['10', '9', '8', '7']),
            ('{1..5..2}', ['1', '3', '5']),
            ('{5..1..2}', ['5', '3', '1']),
            ('{07..10}', ['07', '08', '09', '10']),
            ('{7..010}', ['007', '008', '009', '010']),
            ('{a..e}', ['a', 'b', 'c', 'd', 'e']),
            ('{a..e..2}', ['a', 'c', 'e']),
            ('{e..a}', ['e', 'd', 'c', 'b', 'a']),
            ('{e..a..2}', ['e', 'c', 'a']),
            ('{1..a}', ['{1..a}']),
            ('{a..1}', ['{a..1}']),
            ('{1..1}', ['1']),
            ('{a..a}', ['a']),
            ('{,}', ['', '']),
            ('{Z..a}', ['Z', 'a']),
            ('{a..Z}', ['a', 'Z']),
    ]

    unbalanced_tests = [
            # Unbalanced braces
            '{{1,2}',  # Bash: {1 {2
            '{1,2}}',  # Bash: 1} 2}
            '{1},2}',  # Bash: 1} 2
            '{1,{2}',  # Bash: {1,{2}
            '{}1,2}',  # Bash: }1 2
            '{1,2{}',  # Bash: {1,2{}
            '}{1,2}',  # Bash: }1 }2
            '{1,2}{',  # Bash: 1{ 2{
    ]

    escape_tests = [
            ('\\{1,2\\}', ['{1,2}']),
            ('{1\\,2}',   ['{1,2}']),

            ('\\}{1,2}', ['}1', '}2']),
            ('\\{{1,2}', ['{1', '{2']),
            ('{1,2}\\}', ['1}', '2}']),
            ('{1,2}\\{', ['1{', '2{']),

            ('{\\,1,2}', [',1', '2']),
            ('{1\\,,2}', ['1,', '2']),
            ('{1,\\,2}', ['1', ',2']),
            ('{1,2\\,}', ['1', '2,']),

            ('\\\\{1,2}', ['\\1', '\\2']),

            ('\\{1..2\\}', ['{1..2}']),
    ]

    no_escape_tests = [
            ('\\{1,2}', ['\\1', '\\2']),
            ('{1,2\\}', ['1', '2\\']),
            ('{1\\,2}', ['1\\', '2']),

            ('{\\,1,2}', ['\\', '1', '2']),
            ('{1\\,,2}', ['1\\', '', '2']),
            ('{1,\\,2}', ['1', '\\', '2']),
            ('{1,2\\,}', ['1', '2\\', '']),

            ('\\{1..2\\}', ['\\{1..2\\}']),
    ]

    def test_braceexpand(self):
        for pattern, expected in self.tests:
            result = list(braceexpand(pattern))
            self.assertEqual(expected, result)

    def test_braceexpand_unbalanced(self):
        for pattern in self.unbalanced_tests:
            self.assertRaises(UnbalancedBracesError, braceexpand, pattern)

    def test_braceexpand_escape(self):
        for pattern, expected in self.escape_tests:
            result = list(braceexpand(pattern, escape=True))
            self.assertEqual(expected, result)

    def test_braceexpand_no_escape(self):
        for pattern, expected in self.no_escape_tests:
            result = list(braceexpand(pattern, escape=False))
            self.assertEqual(expected, result)

    def test_zero_padding(self):
        result = braceexpand('{01..1000}')
        self.assertEqual(next(result), '0001')


if __name__ == '__main__':
    unittest.main()
