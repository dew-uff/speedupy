import sys, os
sys.path.append(os.path.dirname(__file__))

from constantes import Constantes

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

else:
    import subprocess
    from entities.Experiment import Experiment
    from services.experiment_service import create_experiment, copy_experiment, create_experiment_function_graph, decorate_experiment_functions_for_execution, get_experiment_functions_hashes, prepare_experiment_main_script_for_inference, update_main_script_file
    from environment import init_env
    from util import save_json_file, copy_to_temp_folder, copy_from_temp_folder, serialize_to_file

    def initialize_intpy(user_script_path):
        def decorator(f):
            def execution(*method_args, **method_kwargs):
                experiment = _initialize_cache(user_script_path)
                _copy_input()
                os.system(f"cd {Constantes().TEMP_FOLDER}; python {' '.join(sys.argv)}")
                _copy_output()
                _start_function_inference_engine(experiment)
            return execution
        return decorator

    def _initialize_cache(user_script_path:str) -> Experiment:
        init_env()
        experiment = create_experiment(user_script_path)
        exp_func_graph = create_experiment_function_graph(experiment)
        functions2hashes = get_experiment_functions_hashes(exp_func_graph)
        experiment.functions2hashes = functions2hashes
        decorate_experiment_functions_for_execution(experiment)
        copy_experiment(experiment)
        save_json_file(functions2hashes, Constantes().EXP_FUNCTIONS_FILENAME)
        serialize_to_file(experiment, Constantes().EXP_SERIALIZED_FILENAME)
        return experiment

    def _copy_input() -> None:
        for input in Constantes().g_argsp_inputs:
            copy_to_temp_folder(input, os.path.isfile(input))
            
    def _copy_output() -> None:
        for output in Constantes().g_argsp_outputs:
            temp_path = os.path.join(Constantes().TEMP_FOLDER, output)
            copy_from_temp_folder(output, os.path.isfile(temp_path))

    def _start_function_inference_engine(experiment:Experiment) -> None:
        prepare_experiment_main_script_for_inference(experiment)
        update_main_script_file(experiment)
        abs_temp_path = os.path.join(os.getcwd(), Constantes().TEMP_FOLDER)
        subprocess.Popen(["python"] + sys.argv, cwd=abs_temp_path)