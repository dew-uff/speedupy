import os
import sys

project_folder = os.path.realpath(__file__).split("setup_exp/")[0]
sys.path.append(project_folder)

# The imports below need the project folder on sys.path, which the two lines
# above set up: the script runs as `python setup_exp/setup.py`, where the
# project root is not on the path.
from constantes import Constantes  # noqa: E402
from setup_exp.services.environment_service import init_env  # noqa: E402
from setup_exp.services.experiment_service import (  # noqa: E402
    analyze_experiment_function_call_hierarchy,
    create_experiment,
    decorate_experiment_functions,
    get_experiment_functions_hashes,
    overwrite_decorated_experiment,
)
from util import check_python_version, save_json_file  # noqa: E402


def validate_main_script_specified():
    if len(sys.argv) != 2:
        raise Exception(
            "Please specify only the main script of your experiment!\nCommand: python setup.py MAIN_SCRIPT.py"
        )


def setup_experiment(main_script_path: str) -> None:
    init_env()
    experiment = create_experiment(main_script_path)
    exp_func_graph = analyze_experiment_function_call_hierarchy(experiment)
    functions2hashes = get_experiment_functions_hashes(exp_func_graph)
    decorate_experiment_functions(experiment)
    overwrite_decorated_experiment(experiment)
    save_json_file(functions2hashes, Constantes().EXP_FUNCTIONS_FILENAME)


if __name__ == "__main__":
    check_python_version()
    validate_main_script_specified()

    setup_experiment(sys.argv[1])
