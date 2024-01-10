import unittest, unittest.mock, os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from data_access import get_already_classified_functions, Constantes

class TestDataAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.system("rm -rf .intpy")
        os.mkdir(".intpy")
        cls.get_already_classified_functions = lambda self: get_already_classified_functions()
        cls.conexaoBanco = Constantes().CONEXAO_BANCO
        stmt = "CREATE TABLE IF NOT EXISTS CLASSIFIED_FUNCTIONS (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        function_hash TEXT NOT NULL,\
        classification TEXT NOT NULL\
        );"
        cls.conexaoBanco.executarComandoSQLSemRetorno(stmt)

    @classmethod
    def tearDownClass(cls):
        cls.conexaoBanco.fecharConexao()
        os.system("rm -rf .intpy")

    def tearDown(self):
        self.conexaoBanco.executarComandoSQLSemRetorno("DELETE FROM CLASSIFIED_FUNCTIONS WHERE id IS NOT NULL;")

    def test_get_already_classified_functions_with_zero_classified_functions(self):
        functions = self.get_already_classified_functions()
        self.assertDictEqual({}, functions)

    def test_get_already_classified_functions_with_CACHE_and_DONT_CACHE_functions(self):
        f1 = hash('def f1():\n\treturn "f1"')
        f2 = hash('def f2(a):\n\treturn a ** 2')
        f3 = hash('def f3(x, y):\n\treturn x/y')
        f4 = hash('def f4():\n\treturn "f4"')
        self.conexaoBanco.executarComandoSQLSemRetorno(f"INSERT INTO CLASSIFIED_FUNCTIONS(function_hash, classification) VALUES ('{f1}', 'CACHE'), ('{f2}', 'CACHE'), ('{f3}', 'DONT_CACHE'), ('{f4}', 'DONT_CACHE');")
        self.conexaoBanco.salvarAlteracoes()

        functions = self.get_already_classified_functions()
        expected_functions = {f'{f1}':'CACHE',
                              f'{f2}':'CACHE',
                              f'{f3}':'DONT_CACHE',
                              f'{f4}':'DONT_CACHE'}
        self.assertDictEqual(expected_functions, functions)
        
if __name__ == '__main__':
    unittest.main()