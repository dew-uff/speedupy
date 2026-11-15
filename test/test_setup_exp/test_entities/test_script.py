import unittest

from setup_exp.entities.Script import Script


class TestScriptDefaults(unittest.TestCase):
    def test_default_functions_are_not_shared_between_scripts(self):
        first = Script("first.py")
        first.functions["f"] = object()

        second = Script("second.py")

        self.assertEqual(second.functions, {})

    def test_default_import_commands_are_not_shared_between_scripts(self):
        first = Script("first.py")
        first.import_commands.add("import os")

        second = Script("second.py")

        self.assertEqual(second.import_commands, set())

    def test_given_arguments_are_kept(self):
        functions = {"f": object()}
        import_commands = {"import os"}

        script = Script("a.py", None, import_commands, functions)

        self.assertIs(script.functions, functions)
        self.assertIs(script.import_commands, import_commands)


if __name__ == "__main__":
    unittest.main()
