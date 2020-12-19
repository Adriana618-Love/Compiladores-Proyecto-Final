from parser import Tokenizer, Validator, Grammar, File
from interpreter import Scope, VideoFileClip
import unittest

FILE_DIRECTORY = 'test_files'


class TestTokenizer(unittest.TestCase):
    def setUp(self):
        Tokenizer.tokens = []
        Tokenizer.errors = []
        super().setUp()

    def tearDown(self):
        Tokenizer.tokens = []
        Tokenizer.errors = []
        super().tearDown()

    def compare_tokens(self, tokens, value_tokens, type_tokens):
        self.assertEqual(len(tokens), len(value_tokens))
        self.assertEqual(len(tokens), len(type_tokens))
        for idx_token, token in enumerate(tokens):
            self.assertEqual(token.item, value_tokens[idx_token])
            self.assertEqual(token.type, type_tokens[idx_token])


    def test_basic_operation(self):
        tokens = Tokenizer('{}/{}'.format(FILE_DIRECTORY, 'test_tokenizer.txt')).tokens
        value_tokens = ['set', 'x', '(', '3', ')', ';', '$']
        type_tokens = ['set', 'variable', '(', 'number', ')', ';', '$']
        self.compare_tokens(tokens, value_tokens, type_tokens)


    def test_video_declaration(self):
        tokens = Tokenizer('{}/{}'.format(FILE_DIRECTORY, 'test_tokenizer_video.txt')).tokens
        value_tokens = ['d_video', 'video', '(', "'videos/video.mp4'", ')', ';', '$']
        type_tokens = ['d_video', 'variable', '(', 'string', ')', ';', '$']
        self.compare_tokens(tokens, value_tokens, type_tokens)


class TestParsingInterpret(unittest.TestCase):
    def setUp(self):
        Tokenizer.tokens = []
        Tokenizer.errors = []
        file = File('rules.txt')
        self.grammar = Grammar()
        self.grammar.set_init('S')
        self.grammar.load(file, '@', '::=')
        self.grammar.get_firsts()
        self.grammar.get_nexts()
        self.grammar.create_table()
        self.validator = Validator(self.grammar.terminals, self.grammar.tas, 'S')
        Scope = {}
        super().setUp()

    def tearDown(self):
        Tokenizer.tokens = []
        Tokenizer.errors = []
        super().tearDown()

    def parse(self, tokens):
        parse_tree, is_valid = self.validator.validate(tokens)
        print('\n', parse_tree)
        if not is_valid:
            raise Exception('Input is not accepted by rules')
        return parse_tree

    def test_basic_operation(self):
        tokens = Tokenizer('{}/{}'.format(FILE_DIRECTORY, 'test_tokenizer.txt')).tokens
        parser_tree = self.parse(tokens)
        parser_tree.interpret()
        self.assertIsNotNone(Scope.get('x'))
        self.assertTrue(type(Scope.get('x')) is int)

    def test_video_declaration(self):
        tokens = Tokenizer('{}/{}'.format(FILE_DIRECTORY, 'test_tokenizer_video.txt')).tokens
        parser_tree = self.parse(tokens)
        parser_tree.interpret()
        self.assertIsNotNone(Scope.get('video'))
        self.assertTrue(type(Scope.get('video')) is VideoFileClip)


if __name__ == '__main__':
    unittest.main()
