class Experiment():
    def __init__(self, experiment_base_dir):
        self.__base_dir = experiment_base_dir
        self.__scripts = {}
    

    def add_script(self, script):
        self.__scripts[script.name] = script
    

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
