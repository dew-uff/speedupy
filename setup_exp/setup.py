import argparse
import os
import sys

project_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(project_folder)

# The imports below need the project folder on sys.path, which the two lines
# above set up: the script runs as `python setup_exp/setup.py`, where the
# project root is not on the path.
from constants import Constants  # noqa: E402
from execute_exp.parser_params import (  # noqa: E402
    EXEC_MODES,
    EXPERIMENTAL_EXEC_MODES,
    STORAGE_OPTIONS,
)
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
    if len(parse_args().main_script) != 1:
        raise Exception(
            "Please specify only the main script of your experiment!\nCommand: python setup.py [-s STORAGE] [--exec-mode MODE] MAIN_SCRIPT.py"
        )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        usage="python setup.py [-s STORAGE] [--exec-mode MODE] MAIN_SCRIPT.py",
        description="Prepare an experiment to run with SpeeduPy.",
    )
    parser.add_argument(
        "main_script", nargs="*", help="the main script of the experiment"
    )
    parser.add_argument(
        "-s",
        "--storage",
        choices=STORAGE_OPTIONS,
        default="file",
        help="the storage to prepare, one of the execution's: "
        + ", ".join(STORAGE_OPTIONS)
        + " (default: file)",
    )
    parser.add_argument(
        "--exec-mode",
        choices=EXEC_MODES,
        default="manual",
        help="the execution mode the experiment will run in, one of the "
        "execution's: "
        + ", ".join(EXEC_MODES)
        + " (default: manual). Only "
        + ", ".join(EXPERIMENTAL_EXEC_MODES)
        + " (experimental, see docs/experimental.md) mark functions with"
        " @maybe_deterministic",
    )
    return parser.parse_args(sys.argv[1:] if argv is None else argv)


def setup_experiment(
    main_script_path: str, storage: str = "file", exec_mode: str = "manual"
) -> None:
    init_env(storage)
    experiment = create_experiment(main_script_path)
    exp_func_graph = analyze_experiment_function_call_hierarchy(experiment)
    functions2hashes = get_experiment_functions_hashes(exp_func_graph)
    decorate_experiment_functions(experiment, exec_mode)
    overwrite_decorated_experiment(experiment)
    save_json_file(functions2hashes, Constants().EXP_FUNCTIONS_FILENAME)
    save_json_file({"exec_mode": exec_mode}, Constants().EXP_SETUP_MODE_FILENAME)


if __name__ == "__main__":
    check_python_version()
    validate_main_script_specified()

    args = parse_args()
    setup_experiment(args.main_script[0], args.storage, args.exec_mode)
