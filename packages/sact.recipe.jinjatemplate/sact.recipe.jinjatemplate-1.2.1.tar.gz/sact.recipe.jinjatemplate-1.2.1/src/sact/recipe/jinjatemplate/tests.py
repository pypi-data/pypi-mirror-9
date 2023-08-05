import os
import unittest


class TestRecipe(unittest.TestCase):

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    result_dir = os.path.abspath(os.path.join(CURRENT_DIR, "templates"))

    def test_simple(self):
        file_1_path = os.path.join(self.result_dir, "test1.result")
        file_2_path = os.path.join(self.result_dir, "test2.result")

        file_1 = open(file_1_path).read()
        file_2 = open(file_2_path).read()

        self.assertEquals(file_1, file_2)

    def test_shell(self):
        file_shell_path = os.path.join(self.result_dir, "test_shell.result")
        result = open(file_shell_path).read()

        expected_without_quote = "; rm -rf /*"
        expected_with_quote = "'; rm -rf /*'"

        result_lines = result.split('\n')
        self.assertEquals(result_lines[0], expected_without_quote)
        self.assertEquals(result_lines[1], expected_with_quote)

    def test_builtins(self):
        file_path = os.path.join(self.result_dir, "test_builtins.result")
        result = open(file_path).read()
        expected = "True"
        self.assertEquals(result, expected)
