class Experiment():
    def __init__(self, experiment_base_dir):
        self.__base_dir = experiment_base_dir
        self.__scripts = {}
        self.__main_script = None
    

    def add_script(self, script):
        self.__scripts[script.name] = script
    

    def set_main_script(self, main_script):
        self.__main_script = main_script


    #####DEBUG#####
    def print(self):
        print("###EXPERIMENT###")
        print("base_dir:", self.__base_dir)
        print("scripts:")
        for script in self.__scripts.values():
            script.print()


    @property
    def base_dir(self):
        return self.__base_dir


    @property
    def scripts(self):
        return self.__scripts

    
    @property
    def main_script(self):
        return self.__main_script
