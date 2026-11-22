import argparse
import sys, os
project_folder = os.path.realpath(__file__).split('setup_exp/')[0]
sys.path.append(project_folder)

from constantes import Constantes
from setup_exp.services.experiment_service import create_experiment, overwrite_decorated_experiment, create_experiment_function_graph, decorate_experiment_functions, get_experiment_functions_hashes
from setup_exp.services.environment_service import init_env
from util import save_json_file, serialize_to_file, check_python_version
    
EXEC_MODES = ['no-cache', 'manual', 'accurate', 'probabilistic-counting', 'probabilistic-error']

def parse_args(argv=None):
    parser = argparse.ArgumentParser(usage='python setup.py [--exec-mode MODE] MAIN_SCRIPT.py',
                                     description='Prepare an experiment to run with SpeeduPy.')
    parser.add_argument('main_script', nargs=1, help='the main script of the experiment')
    parser.add_argument('--exec-mode', choices=EXEC_MODES, default='manual',
                        help='the execution mode the experiment will run with (default: manual). '
                             'Only accurate and probabilistic-* mark functions with @maybe_deterministic, '
                             'an experimental feature.')
    return parser.parse_args(sys.argv[1:] if argv is None else argv)

def setup_experiment(main_script_path:str, exec_mode:str='manual') -> None:
    init_env()
    experiment = create_experiment(main_script_path)
    exp_func_graph = create_experiment_function_graph(experiment)
    functions2hashes = get_experiment_functions_hashes(exp_func_graph)
    decorate_experiment_functions(experiment, exec_mode)
    overwrite_decorated_experiment(experiment)
    save_json_file(functions2hashes, Constantes().EXP_FUNCTIONS_FILENAME)
    serialize_to_file(experiment, Constantes().EXP_SERIALIZED_FILENAME)

if __name__ == '__main__':
    check_python_version()
    args = parse_args()
    setup_experiment(args.main_script[0], args.exec_mode)