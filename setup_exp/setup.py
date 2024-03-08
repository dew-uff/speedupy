import sys, os
project_folder = os.path.realpath(__file__).split('setup_exp/')[0]
sys.path.append(project_folder)

from constantes import Constantes
from setup_exp.services.experiment_service import create_experiment, overwrite_decorated_experiment, create_experiment_function_graph, decorate_experiment_functions, get_experiment_functions_hashes
from setup_exp.services.environment_service import init_env
from util import save_json_file, serialize_to_file, check_python_version
    
def validate_main_script_specified():
    if len(sys.argv) != 2:
        raise Exception('Please specify only the main script of your experiment!\nCommand: python setup.py MAIN_SCRIPT.py')

def setup_experiment(main_script_path:str) -> None:
    init_env()
    experiment = create_experiment(main_script_path)
    exp_func_graph = create_experiment_function_graph(experiment)
    functions2hashes = get_experiment_functions_hashes(exp_func_graph)
    decorate_experiment_functions(experiment)
    overwrite_decorated_experiment(experiment)
    save_json_file(functions2hashes, Constantes().EXP_FUNCTIONS_FILENAME)
    serialize_to_file(experiment, Constantes().EXP_SERIALIZED_FILENAME)

if __name__ == '__main__':
    check_python_version()
    validate_main_script_specified()
    
    setup_experiment(sys.argv[1])