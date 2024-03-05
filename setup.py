import sys, os
sys.path.append(os.path.dirname(__file__))

from constantes import Constantes
from entities.Experiment import Experiment
from services.experiment_service import create_experiment, copy_experiment, create_experiment_function_graph, decorate_experiment_functions_for_execution, get_experiment_functions_hashes
from environment import init_speedupy_env
from util import save_json_file, serialize_to_file

def check_python_version():
    if sys.version_info[0] != 3 or sys.version_info[1] < 9:
        raise Exception('Requires python 3.9+')
    
def validate_main_script_specified():
    if len(sys.argv) != 2:
        raise Exception('Please specify only the main script of your experiment!\nCommand: python setup.py MAIN_SCRIPT.py')

def setup_experiment(main_script_path:str) -> Experiment:
    init_speedupy_env()
    experiment = create_experiment(main_script_path)
    exp_func_graph = create_experiment_function_graph(experiment)
    functions2hashes = get_experiment_functions_hashes(exp_func_graph)
    decorate_experiment_functions_for_execution(experiment)
    copy_experiment(experiment)
    save_json_file(functions2hashes, Constantes().EXP_FUNCTIONS_FILENAME)
    serialize_to_file(experiment, Constantes().EXP_SERIALIZED_FILENAME)
    return experiment

if __name__ == '__main__':
    check_python_version()
    validate_main_script_specified()
    
    setup_experiment(sys.argv[1])