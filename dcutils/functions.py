
def parse_args(argv:list):

    # Define arguments dictionaries
    args_dict = {}

    # Pass data to dictionary
    for arg in argv[1:]:
        
        key, value = arg.split('=')
        args_dict[key] = value

    return args_dict