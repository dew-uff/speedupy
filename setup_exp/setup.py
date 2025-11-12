import sys, os
import argparse
project_folder = os.path.realpath(__file__).split('setup_exp/')[0]
sys.path.append(project_folder)

from constantes import Constantes
from setup_exp.services.experiment_service import create_experiment, overwrite_decorated_experiment, analyze_experiment_function_call_hierarchy, decorate_experiment_functions, get_experiment_functions_hashes
from setup_exp.services.environment_service import init_env
from util import save_json_file, check_python_version
    
def parse_arguments():
    parser = argparse.ArgumentParser(description="SpeeduPy Experiment Setup Utility.")
    
    # Argumento posicional: o script principal
    parser.add_argument('main_script_path', type=str, 
                        help='The path to the main script of your experiment (MAIN_SCRIPT.py).')

    # Argumento opcional: o storage 
    parser.add_argument('-s', '--storage', type=str, default='file',
                        choices=['file', 'sqlite', 'redis', 'mongo', 'mysql'],
                        help='Define which storage backend to initialize. Default is "file".')

    return parser.parse_args()


def setup_experiment(args) -> None:
    # Passa o storage_type para init_env
    init_env(args.storage) 
    
    main_script_path = args.main_script_path 
    
    experiment = create_experiment(main_script_path)
    exp_func_graph = analyze_experiment_function_call_hierarchy(experiment)
    functions2hashes = get_experiment_functions_hashes(exp_func_graph)
    decorate_experiment_functions(experiment)
    overwrite_decorated_experiment(experiment)
    save_json_file(functions2hashes, Constantes().EXP_FUNCTIONS_FILENAME)

if __name__ == '__main__':
    check_python_version()
    args = parse_arguments()    # 1. Parseia e valida os argumentos
    setup_experiment(args)      # 2. Chama o setup com os argumentos parsed