import os
from typing import List

from entities.Script import Script
from entities.Experiment import Experiment
from entities.FunctionGraph import FunctionGraph

from services.script_service import create_script, create_script_function_graph
from util import get_all_init_scripts_implicitly_imported, is_an_user_defined_script

def create_experiment(user_script_path:str) -> Experiment:
    experiment_base_dir, user_script_name = os.path.split(user_script_path)
    experiment = Experiment(experiment_base_dir)
    scripts_analized = []
    scripts_to_be_analized = [user_script_name]
    while(len(scripts_to_be_analized) > 0):
        script_name = scripts_to_be_analized.pop(0)
        script = create_script(script_name, experiment.base_dir)
        if(script_name == user_script_name):
            script.name = "__main__"
        experiment.add_script(script)
        __update_scripts_to_be_analized(script, scripts_analized, scripts_to_be_analized, experiment.base_dir)
        scripts_analized.append(script_name)
    return experiment

def __update_scripts_to_be_analized(script:Script, scripts_analized:List[str], scripts_to_be_analized:List[str], experiment_base_dir:str):
    imported_scripts = script.get_imported_scripts()        
    for imp_script in imported_scripts:
        if __script_needs_to_be_analyzed(imp_script, experiment_base_dir, scripts_analized):
            scripts_to_be_analized.append(imp_script)

            init_scripts = get_all_init_scripts_implicitly_imported(imp_script, experiment_base_dir)
            for i_script in init_scripts:
                if __script_needs_to_be_analyzed(i_script, experiment_base_dir,scripts_analized):
                    scripts_to_be_analized.append(i_script)

def __script_needs_to_be_analyzed(script:str, experiment_base_dir:str, scripts_analized:List[str]) -> bool:
    return is_an_user_defined_script(script, experiment_base_dir) and \
            not __script_already_analized(script, scripts_analized)

def __script_already_analized(script_name:str, scripts_analized:List[:str]) -> bool:
    return script_name in scripts_analized
    
def create_experiment_function_graph(experiment:Experiment) -> FunctionGraph:
    create_script_function_graph("__main__")
    script = experiment.scripts["__main__"]
    return script.function_graph
