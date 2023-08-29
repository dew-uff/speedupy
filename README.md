# Speedupy
This tool was developed to speed up the execution time of programs written in Python, using a memoization-based approach applied to pure functions.

## How to use?

### Prepare the directories

Go to the folder where the programs you want to accelerate are located.
```bash
$ cd </program_folders_path>

</program_folders_path>$ git clone https://github.com/dew-uff/speedupy.git
```
In our case, the [speedupy_experiments-main](https://github.com/dew-uff/speedupy_experiments) folder was used, which can be obtained to test the tool by clicking on the link, after that, just unzip it.
```bash
$ cd Downloads/speedupy_experiments-main/01pilots/01pilots_exp01_fibonacci

~/Downloads/speedupy_experiments-main/01pilots/01pilots_exp01_fibonacci $ git clone https://github.com/dew-uff/speedupy.git
```

### Prepare the files
For the tool to be able to interpret the experiment code, denote it with the following decorators:

* @deterministic - for each pure function that will be accelerated
* @initialize_intpy(\_\_file\_\_) - to the main function

In addition, it is necessary to have the following structure to call the main function:
* if __name__ =="\_\_main\_\_":
     </br>n = int(sys.argv[1])
     </br>start = time.perf_counter()
     </br>main(n)
     </br>print(time.perf_counter()-start)

* Adaptation may be necessary due to arguments passed as parameters in the main.

Example:

![screen1_speedupy](https://github.com/dew-uff/speedupy/assets/18330758/35d7db61-1e9a-405f-ae78-bea5e6903d75)

Figure 1: Code adapted from the nth Fibonacci term calculation.


![screen2_speedupy](https://github.com/dew-uff/speedupy/assets/18330758/ec32db82-8ed2-4bab-b6bb-f53d2ab46b6d)

Figure 2: Code adapted from the calculation of power, from a number n, to m.

### Running the programs
Once the program is already adapted, just run it.
```bash
$ python <filename>.py program_params [-h, --help] [-g, --glossary] [-m memory|help, --memory memory|help] [-0, --no-cache] [- H type|help, --hash type|help] [-M method|help, --marshalling method|help] [-s form|help, --storage form|help]
```
To get an overview, just use the "-h" or "--help" argument and you will have all the valid arguments and their entries.
```bash
python fibonacci.py -h
```

![screen3_speedupy](https://github.com/dew-uff/speedupy/assets/18330758/8b154302-8d80-460b-a16d-3a6b837aa58e)

Figure 3: Use of the general help with -h.


Once the arguments and their respective parameters have been discovered, we can use them as shown in the image below:

![screen4_speedupy](https://github.com/dew-uff/speedupy/assets/18330758/017d0839-084e-4e01-a69c-65e60c2c772f)

Figure 4: Example of defining some arguments.

Finally, if you want to know more about a specific argument, use the "help" after this argument:

![screen5_speedupy](https://github.com/dew-uff/speedupy/assets/18330758/be602515-fb86-4191-8f9c-bdca80405348)

Figure 5: Use of the arguments's help.


