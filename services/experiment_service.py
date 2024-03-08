from typing import Dict

from entities.Experiment import Experiment
from services.script_service import classify_script_functions

def classify_experiment_functions(experiment:Experiment, functions_2_hashes:Dict[str, str]) -> None:
    for script in experiment.scripts.values():
        classify_script_functions(script, functions_2_hashes)
    