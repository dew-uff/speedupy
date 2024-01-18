import os, ast
from typing import List, Dict

from entities.Script import Script
from entities.Experiment import Experiment
from entities.FunctionGraph import FunctionGraph
from data_access import get_already_classified_functions, get_id
from services.script_service import create_script, create_script_function_graph, decorate_script_functions, copy_script, add_decorator_imports, classify_script_functions
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
            experiment.set_main_script(script)
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

def __script_already_analized(script_name:str, scripts_analized:List[str]) -> bool:
    return script_name in scripts_analized
    
def create_experiment_function_graph(experiment:Experiment) -> FunctionGraph:
    create_script_function_graph(experiment.main_script, experiment)
    script = experiment.main_script
    return script.function_graph

def get_experiment_functions_hashes(experiment_function_graph:FunctionGraph) -> Dict[str, str]:
    functions2hashes = {}
    for vertice in experiment_function_graph.graph:
        source_code = experiment_function_graph.get_source_code_executed(vertice)
        hash = get_id(source_code)
        functions2hashes[vertice.qualname] = hash
    return functions2hashes

def decorate_experiment_functions(experiment:Experiment) -> None:
    classified_functions = get_already_classified_functions()
    for script in experiment.scripts.values():
        add_decorator_imports(script)
        decorate_script_functions(script, classified_functions, experiment.functions2hashes)
    _decorate_experiment_main_function(experiment)

def _decorate_experiment_main_function(experiment:Experiment):
    main_script = experiment.main_script
    for func in main_script.functions.values():
        for decorator in func.decorator_list:
            if isinstance(decorator, ast.Call) and \
               isinstance(decorator.func, ast.Name) and \
               decorator.func.id == 'initialize_intpy':
                func.decorator_list.remove(decorator)
                func.decorator_list.append(ast.Name(id='execute_intpy', ctx=ast.Load()))
                return

def copy_experiment(experiment:Experiment):
    for script in experiment.scripts.values():
        copy_script(script)

def classify_experiment_functions(experiment:Experiment, functions_2_hashes:Dict[str, str]) -> None:
    for script in experiment.scripts.values():
        classify_script_functions(script, functions_2_hashes)