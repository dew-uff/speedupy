import sys, os
sys.path.append(os.path.dirname(__file__))

from constantes import Constantes
from environment import init_env

init_env()

def check_python_version():
    if sys.version_info[0] != 3 or sys.version_info[1] < 9:
        raise Exception('Requires python 3.9+')

def validate_user_args():
    if Constantes().g_argsp_m == None and not Constantes().g_argsp_no_cache:
        print("Error: enter the \"-h\" parameter on the command line after \"python script.py\" to see usage instructions")
        sys.exit()

check_python_version()
validate_user_args()

if Constantes().g_argsp_no_cache:
    #On the decorator "initialize_intpy", "user_script_path" is declared
    #to maintain compatibility
    def initialize_intpy(user_script_path):
        def decorator(f):
            def execution(*method_args, **method_kwargs):
                f(*method_args, **method_kwargs)
            return execution
        return decorator


    def deterministic(f):
        return f
else:
    from services.experiment_service import create_experiment, copy_experiment, create_experiment_function_graph, decorate_experiment_functions, get_experiment_functions_hashes
    from util import save_json_file

    def initialize_intpy(user_script_path):
        def decorator(f):
            def execution(*method_args, **method_kwargs):
                _initialize_cache(user_script_path)
                os.system(f"cd {Constantes().TEMP_FOLDER}; python {' '.join(sys.argv)}")
                _copy_output()
            return execution
        return decorator


    def _initialize_cache(user_script_path):
        experiment = create_experiment(user_script_path)
        exp_func_graph = create_experiment_function_graph(experiment)
        functions2hashes = get_experiment_functions_hashes(exp_func_graph)
        decorate_experiment_functions(experiment)
        copy_experiment(experiment)
        save_json_file(functions2hashes, Constantes().EXP_FUNCTIONS_FILENAME)

    #TODO
    def _copy_output(): pass