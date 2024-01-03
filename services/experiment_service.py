import os

from entities.Script import Script
from entities.Experiment import Experiment

from services.script_service import create_script
from util import get_all_init_scripts_implicitly_imported, is_an_user_defined_script

class ExperimentService():
    def create_experiment(self, user_script_path:str) -> Experiment:
        experiment_base_dir, user_script_name = os.path.split(user_script_path)
        self.__experiment = Experiment(experiment_base_dir)
        self.__scripts_analized = []
        self.__scripts_to_be_analized = [user_script_name]
        while(len(self.__scripts_to_be_analized) > 0):
            script_name = self.__scripts_to_be_analized.pop(0)
            script = create_script(script_name, self.__experiment.base_dir)
            if(script_name == user_script_name):
                script.name = "__main__"
            self.__experiment.add_script(script)
            self.__update_scripts_to_be_analized(script)
            self.__scripts_analized.append(script_name)
        return self.__experiment

    def __update_scripts_to_be_analized(self, script:Script):
        imported_scripts = script.get_imported_scripts()        
        for imp_script in imported_scripts:
            if self.__script_needs_to_be_analyzed(imp_script):
                self.__scripts_to_be_analized.append(imp_script)

                init_scripts = get_all_init_scripts_implicitly_imported(imp_script, self.__experiment.base_dir)
                for i_script in init_scripts:
                    if self.__script_needs_to_be_analyzed(i_script):
                        self.__scripts_to_be_analized.append(i_script)

    def __script_needs_to_be_analyzed(self, script:str) -> bool:
        return is_an_user_defined_script(script, self.__experiment.base_dir) and \
               not self.__script_already_analized(script)

    def __script_already_analized(self, script_name:str) -> bool:
        return script_name in self.__scripts_analized
    
