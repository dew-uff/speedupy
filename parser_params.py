import argparse
import sys


def usage_msg():
    return "\nSpeeduPy's command line arguments help:\n\n\
To run your experiment with SpeeduPy use:\n\
$ python "+str(sys.argv[0])+" program_arguments [-h, --help] [-g, --glossary] [-m memory|help, --memory memory|help] [-H type|help, --hash type|help] [-M method|help, --marshalling method|help] [-s form|help, --storage form|help]\n\n\
To run in the SpeeduPy DEBUG mode use:\n\
$ DEBUG=True python "+str(sys.argv[0])+" program_arguments [-h, --help] [-g, --glossary] [-m memory|help, --memory memory|help] [-H type|help, --hash type|help] [-M method|help, --marshalling method|help] [-s form|help, --storage form|help]\n\n\
"
def glossary_msg():
    return exec_mode_msg() + strategy_msg() + hashes_msg() + marshalling_msg() + storage_msg() + memory_msg()

def exec_mode_msg():
    return "\nExecution Mode - Defines how SpeeduPy will execute:\n\
    =>no-cache      : SpeeduPy will cache no functions\n\
    =>manual        : SpeeduPy only caches the functions annotated by the user with @deterministic\n\
    =>accurate      : SpeeduPy looks for statistically pure functions and only caches function calls that always returned the same output\n\
    =>probabilistic : SpeeduPy looks for statistically pure functions and caches function calls that sometimes returned different outputs, according to the policy set on --strategy param\n"

def strategy_msg():
    return "\nStrategy - Defines SpeeduPy\'s policy for caching function calls when executing in probabilistic mode\n\
    =>error    : SpeeduPy only caches function calls that introduce errors up to a user-specified limit\n\
    =>counting : SpeeduPy only caches function calls whose most produced output occurred at least a minimum percentage of times defined by the user\n"

def hashes_msg():
    return "\nHashes: \n\
    =>md5   : is a cryptographic hash fuction with a better collision resistence and lower performance compared to the others.\n\
    =>murmur: is a modern non-cryptographic hash function with a low collision rate and high performance.\n\
    =>xxhash: is a modern non-cryptographic hash function with a lower collision resistence and better performance compered to murmur.\n\
    usage: $ python "+str(sys.argv[0])+" program_arguments -H|--hash options\n"

def marshalling_msg():
    return "\nMarshalling:\n\
    =>Pickle:\n\
    usage: $ python "+str(sys.argv[0])+" program_arguments -M|--marshalling options\n"

def storage_msg():
    return "\nStorage:\n\
    =>db-file: use database and file to store data.\n\
    =>db     : use database to store data\n\
    =>file   : use file to store data.\n\
    usage: $ python "+str(sys.argv[0])+" program_arguments -s|--storage options\n"

def memory_msg():
    return "\nMemory forms:\n\
    =>ad      : original version with some bug fixes and instrumentation, all data are stored directly in the database.\n\
    =>1d-ow   : one dicionary (1d), only write (ow), 1st implementation of dictionary: new data is added to the dictionary only when cache miss occur and the function decorated with @deterministic is executed.\n\
    =>1d-ad   : one dicionary (1d), all data loaded at the begining (ad), 2nd implementation of dictionary (uses 1 dictionary): at the begining of the execution all the data cached is loaded to the dictonary before the user script starts to run.\n\
    =>2d-ad   : two dicionaries (2d), all data loaded at the begining (ad), 3rd implementation of dictionary (uses 2 dictionaries): at the begining of the execution all the data cached is loaded to the dictionary DATA_DICTIONARY before the user script starts to run. When cache miss occurs and a function decorated with @deterministic is processed, its result is stored in NEW_DATA_DICTIONARY. This way, only the elements of NEW_DATA_DICTIONARY are added to the database at the end of the execution.\n\
    =>2d-ad-t : two dicionaries (2d), all data loaded at the begining with a thread (ad-t), 4th implementation of dictionary (uses 2 dictionaries): at the begining of the execution a thread is started to load all the data cached in the database to the dictionary DATA_DICTIONARY. When cache miss occurs and a function decorated with @deterministic is processed, its result is stored in NEW_DATA_DICTIONARY. Only the elements of NEW_DATA_DICTIONARY are added to the database at the end of the execution but it is possible that some elements in NEW_DATA_DICTIONARY are already in the database due to the concurrent execution of the experiment and the thread that populates DATA_DICTIONARY.\n\
    =>2d-ad-f : two dicionaries (2d), all data loaded at the begining of a function(ad-f), 5th implementation of dictionary (uses 2 dictionaries): when @deterministic is executed a select query is created to the database to bring all results of the function decorated with @deterministic stored in the cache. A list of functions already inserted to the dictionary is maintained to avoid unecessary querys to the database. The results are then stored in the dictionary DATA_DICTIONARY. When cache miss occurs and a function decorated with @deterministic is processed, its result is stored in NEW_DATA_DICTIONARY. This way, only the elements of NEW_DATA_DICTIONARY are added to the database at the end of the execution.\n\
    =>2d-ad-ft: two dicionaries (2d), all data loaded at the begining of a function with a thread (ad-ft), 6th implementation of dictionary (uses 2 dictionaries): when @deterministic is executed a select query is created to the database to bring all results of the function decorated with @deterministic stored in the cache. A list of functions already inserted to the dictionary is maintained to avoid unecessary querys to the database. The results of the query are stored in the dictionary DATA_DICTIONARY by a thread. When cache miss occurs and a function decorated with @deterministic is processed, its result is stored in NEW_DATA_DICTIONARY. This way, only the elements of NEW_DATA_DICTIONARY are added to the database at the end of the execution.\n\
    =>2d-lz   : two dicionaries (2d), lazy mode (lz), 7th implementation of dictionary (uses 2 dictionaries): new data is added to DATA_DICTIONARY when cache hit occurs (LAZY approach) and new data is added to NEW_DATA_DICTIONARY when cache miss occur and the function decorated with @deterministic is executed.\n\
    usage: $ python "+str(sys.argv[0])+" program_arguments -m|--memory options\n"
    

def get_params():
    memories = ['help','ad', '1d-ow', '1d-ad', '2d-ad', '2d-ad-t', '2d-ad-f', '2d-ad-ft', '2d-lz']
    hashes = ['help','md5', 'murmur', 'xxhash']
    marshals = ['help','pickle']
    storageOptions = ['help','db-file','db','file']
    exec_modes = ['no-cache', 'manual', 'accurate', 'probabilistic']
    prob_mode_strategies = ['counting', 'error']

    speedupy_arg_parser = argparse.ArgumentParser(usage=usage_msg())

    speedupy_arg_parser.add_argument('-g',
                                  '--glossary',
                                  default=False,
                                  action='store_true',
                                  help='show all parameters options')
    
    speedupy_arg_parser.add_argument('args',
                                   metavar='program arguments',
                                   nargs='*',
                                   type=str, 
                                   help='program arguments')
        
    speedupy_arg_parser.add_argument('--exec-mode',
                                  choices=exec_modes,
                                  metavar='',
                                  nargs=1,
                                  default=None,
                                  help='defines how SpeeduPy will execute')
    
    speedupy_arg_parser.add_argument('--strategy',
                                  choices= prob_mode_strategies,
                                  metavar='',
                                  default=None,
                                  nargs=1,
                                  help='defines SpeeduPy\'s policy for caching function calls when executing in probabilistic mode')
    
    speedupy_arg_parser.add_argument('--min-num-exec',
                                  default=20,
                                  type=int,
                                  nargs=1,
                                  help='defines them minimum number of times SpeeduPy\'s must execute a function call before trying to cache it')
    
    speedupy_arg_parser.add_argument('-m',
                                  '--memory',
                                   choices=memories,
                                   metavar='',
                                   nargs=1,
                                   type=str,
                                   default=['2d-ad'],
                                   help='SpeeduPy\'s mechanism of persistence: choose one of the following options: '+', '.join(memories))
    
    speedupy_arg_parser.add_argument('-H',
                                  '--hash',
                                   choices=hashes,
                                   metavar='',
                                   nargs=1,
                                   default=['md5'],
                                   help='SpeeduPy\'s mechanism of hashes: choose one of the following options: '+', '.join(hashes))
    
    speedupy_arg_parser.add_argument('-M',
                                  '--marshalling',
                                   choices=marshals,
                                   metavar='',
                                   nargs=1,
                                   default=['pickle'],
                                   help='SpeeduPy\'s mechanism of marshalling: choose one of the following options: '+', '.join(marshals))
    
    speedupy_arg_parser.add_argument('-s',
                                  '--storage',
                                   choices=storageOptions,
                                   metavar='',
                                   nargs=1,
                                   default=['db-file'],
                                   help='SpeeduPy\'s mechanism of storage: choose one of the following options: '+', '.join(storageOptions))
    
    speedupy_arg_parser.add_argument('-i',
                                  '--inputs',
                                   metavar='FILE/FOLDER',
                                   nargs='*',
                                   default=[],
                                   help='specifies all input files/folders your experiment needs in order to execute correctly')
    
    speedupy_arg_parser.add_argument('-o',
                                  '--outputs',
                                   metavar='FILE/FOLDER',
                                   nargs='*',
                                   default=[],
                                   help='specifies all output files/folders your experiment generates')

    
    args = speedupy_arg_parser.parse_args()

    
    if args.glossary:
        print(glossary_msg())
        sys.exit()

    argsp_exp_args = args.args

    argsp_exec_mode = args.exec_mode
    argsp_strategy = args.strategy
    argsp_min_num_exec = args.min_num_exec
    
    argsp_m = args.memory
    argsp_s = args.storage
    argsp_M = args.marshalling
    argsp_hash = args.hash

    argsp_inputs = args.inputs
    argsp_outputs = args.outputs

    if str(argsp_m[0]) == 'help' or str(argsp_M[0]) == 'help' or str(argsp_hash[0]) == 'help' or str(argsp_s[0]) == 'help':
        if str(argsp_m[0]) == 'help':
            print(memory_msg())
            
        if str(argsp_M[0]) == 'help':
            print(marshalling_msg())

        if str(argsp_hash[0]) == 'help':
            print(hashes_msg())

        if str(argsp_s[0]) == 'help':
            print(storage_msg())
        sys.exit()

    return argsp_exp_args, argsp_m, argsp_M, argsp_s, argsp_exec_mode, argsp_strategy, argsp_min_num_exec, argsp_hash, argsp_inputs, argsp_outputs


"""
if argsp.version == ['1d-ow'] or argsp.version == ['v021x']:
    v_data_access = ".data_access_v021x_1d-ow"
elif argsp.version == ['1d-ad'] or argsp.version == ['v022x']:
    v_data_access = ".data_access_v022x_1d-ad"
elif argsp.version == ['2d-ad'] or argsp.version == ['v023x']:
    v_data_access = ".data_access_v023x_2d-ad"
elif argsp.version == ['2d-ad-t'] or argsp.version == ['v024x']:
    v_data_access = ".data_access_v024x_2d-ad-t"
elif argsp.version == ['2d-ad-f'] or argsp.version == ['v025x']:
    v_data_access = ".data_access_v025x_2d-ad-f"
elif argsp.version == ['2d-ad-ft'] or argsp.version == ['v026x']:
    v_data_access = ".data_access_v026x_2d-ad-ft"
elif argsp.version == ['2d-lz'] or argsp.version == ['v027x']:
    v_data_access = ".data_access_v027x_2d-lz"
else:
    v_data_access = ".data_access_v021x_1d-ow"
"""