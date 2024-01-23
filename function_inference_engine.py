from functools import wraps
from typing import Dict, Tuple
import sys, os
sys.path.append(os.path.dirname(__file__))

from constantes import Constantes
from entities.Experiment import Experiment
from services.experiment_service import classify_experiment_functions
from util import get_content_json_file, deserialize_from_file

def start_inference_engine(f):
    @wraps(f)
    def execution(*method_args, **method_kwargs):
        Constantes().set_paths_for_executing_inside_temp_folder()
        experiment, functions_2_hashes = _get_experiment_and_functions_2_hashes()
        classify_experiment_functions(experiment, functions_2_hashes)
    return execution

def _get_experiment_and_functions_2_hashes() -> Tuple[Experiment, Dict[str, str]]:
    experiment = deserialize_from_file(Constantes().EXP_SERIALIZED_FILENAME)
    functions_2_hashes = get_content_json_file(Constantes().EXP_FUNCTIONS_FILENAME)
    return experiment, functions_2_hashes
