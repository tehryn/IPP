#!/usr/bin/env python3.5
import sys
import re

def debug(s):
    print("------\n" + str(s))

class Arguments:
    """
        Class for storing program arguments.
        Class has these methods:
        __init__(self, arguments)
        __str__(self)
    """
    help         = False         # Tells if --help is in arguments
    input        = sys.stdin     # Stores name of input file
    output       = sys.stdout    # Stores name of output file
    finish       = False         # Tells if --find-non-finishing is in arguments
    minimize     = False         # Tells if --minimize is in arguments
    insensitive  = False         # Tells if --case-insensitive is in arguments

    __input_set  = False         # Tells if --input= was set
    __output_set = False         # Tells if --output= was set
    def __init__(self, arguments):
        """
            Constructor of Class Arguments.
            There is given only one argument, which is list of strings,
            where are stored program arguments for parsing.
        """
        for arg in arguments:
            if arg == "--help" and self.help is False:
                self.help = True
            elif (arg == "-f" or arg == "--find-non-finishing") and self.finish is False:
                self.finish = True
            elif (arg == "-m" or arg == "--minimize") and self.minimize is False:
                self.minimize = True
            elif (arg == "-i" or arg == "--case-insensitive") and self.insensitive is False:
                self.insensitive = True
            elif arg.startswith("--input=") and self.__input_set is False:
                self.input        = arg[8:]
                self.__input_set  = True
            elif arg.startswith("--output=") and self.__output_set is False:
                self.output       = arg[9:]
                self.__output_set = True
            else:
                err("Invalid use of arguments.", 1)
                exit(1)
        self.__valide_arguments(len(arguments))


    def __str__(self):
        """
            Returns both private and public variable names with their values as string
        """
        return ('help:         %s \n'
                'input:        %s \n'
                'output:       %s \n'
                'finish:       %s \n'
                'minimize:     %s \n'
                'insensitive:  %s \n'
                '__input_set:  %s \n'
                '__output_set: %s'
               )%(str(self.help), str(self.input), str(self.output), str(self.finish),
                  str(self.minimize), str(self.insensitive), str(self.__input_set),
                  str(self.__output_set))


    def __valide_arguments(self, num_of_arguments):
        """
            Checks if arguments are valide. Needs number of arguments as parametr.
        """
        if num_of_arguments > 1 and self.help:
            err("You can't just ask for help and insert another argument(s)...", 1)
            exit(1)
        if self.minimize and self.finish:
            err("You can't just use --minimize and --find-non-finishing argument at once...", 1)
            exit(1)


    def print_help():
        """
            Prints program arguments on stdout.
        """
        sys.stdout.write(
            'Usage: python3.6 ./mka.py [--input=filename --output=filename --help -m -f -i]\n\n'
            '--input=filename         Specifies input file. Default value is stdin.\n'
            '--output=filename        Specifies output file. Default value is stdout.\n'
            '--help                   Print this message on stdout.\n'
            '-m, --minimize           Minimize state machine.\n'
            '-f, --find-non-finishing Finds non finishing state of state machine.\n'
            '-i, --case-insensitive   Program will be case insensitive.\n'
        )


def err(message, code):
    """
        Prints error message on stderr and exit program with specific errorcode
    """
    sys.stderr.write(message + "\n")
    exit(code)


def parse_input(args):
    """
        Tries to open input file and parse it.
        Returns dictionary with keys 'states', 'alphabet', 'rules', 'start_state'
        and 'finish state', where 'rules' is list of dictionaries with keys
        'start', 'symbol' and 'next'. All 3 are strings. 'start_state' is
        string and rest are sets.
    """
    try:
        input = args.input
        if (not (input is sys.stdin)):
            input = open(args.input, "r")
        data = input.read()
        input.close()
    except:
        err("Unable to open input file '" + str(args.input) + "' for reading", 2)
    data = prepare_data(data)   # Deletes coments and white characters
    if args.insensitive:        # Check for argument --case-insensitive
        data = data.lower()     # Convert whole input into lowercase
    data = retrieve_data(data)  # Parse input
    return data

def prepare_data(data):
    """
        Deletes all comments and all useless white characters.
    """
    comment     = False # Tells if we are in comment
    apostrophe  = False # Tells if we are between 2 apostrophes
    raw_string = str()  # Variable for storing parsed data

    # Simple state machine where c represents string of length 1
    for c in data:
        if comment:        # If we are in comment, we ignore all characters
            if c == "\n":  # expect end of line.
                comment = False
            continue
        elif not apostrophe and c == "#": # Detecting comments
            comment = True
            continue
        elif c == "'":    # Detecting apostrophes
            if not apostrophe:
                apostrophe = True
            else:
                apostrophe = False
        if(not c.isspace() or (c.isspace() and apostrophe)): # Ignoring white characters
            raw_string += c
    return raw_string


def retrieve_data(data):
    """
        Parses definition of state machine. Definition should be without spaces
        and useless white characters.
        Returns dictionary with keys 'states', 'alphabet', 'rules', 'start_state'
        and 'finish state', where 'rules' is list of dictionaries with keys
        'start', 'symbol' and 'next'. All 3 are strings. 'start_state' is
        string and rest are sets.
    """
    # Dictionary for storing states, alphabet, rules, starting state and
    # finishing state.
    input_data             = {"states":set(), "alphabet":set(), "rules":list(),
                              "start_state":str(), "fin_states":set()}
    # Regex pattern for validing state variable
    pattern                = re.compile(r"[_]{0}[aA-zZ]\w*[_]{0}")

    ident                  = str()  # Variable for temporary storing usefull data
    state                  = -1     # Represents current state of state machine
    next_state             = 0      # Represents next state
    expected_bracket_open  = True   # Tells if expected character is (
    expected_bracket_close = False  # Tells if expected character is )
    expected_brace_open    = False  # Tells if expected character is {
    expected_comma         = False  # Tells if expected character is ,
    expected_apostrophe    = False  # Tells if expected character is '

    data = enumerate(data) # String is not iterable, but function next is used
    # State machine itself. i is index, char is substring of string with length 1
    for i, char in data:
        if state == 0: # State 0 represents loading set of states.
            if expected_brace_open: # Reading opening brase of set
                if char != "{":
                    err("Missing opening brace in input source.", 60)
                expected_brace_open = False
            else:
                ident = ""
                while char != ",":            # Reading state identificator
                    if char == "}":           # Last state in set was read
                        expected_comma = True # Comma need to be inserted
                        state          = -1   # Switching to default state
                        next_state     = 1    # Setting next state
                        break
                    else:
                        ident  += char
                        i, char = next(data)  # Reading next char
                        if char is None:      # End of source was reached
                            err("Invalid imput source.", 60)
                if not pattern.match(ident):  # Testing validity of identificator
                    err("'%s' is invalid name of state."%(ident), 60)
                input_data["states"].add(ident) # Adding state into set
        elif state == 1: # State 1 represents loading alphabet
            if expected_brace_open: # reading opening brace of set
                if char != "{":
                    err("Missing opening brace in input source.", 60)
                expected_brace_open = False
            elif char == "}":    # Set is empty
                err("Input alphabet is empty.", 61)
            else:                # Reading symbol
                if char != "'":  # Symbol is ''
                    err("Missing apostrophe in input source.", 60)
                i, char = next(data)
                if (char == "'"):
                    i, char = next(data)
                    if (char != "'"):
                        err("Invalid member of alphabet.", 60)
                    ident = "''"
                elif char is None: # End of source is reached
                    err("Invalid input source.", 60)
                else:              # Char is nothing special
                    ident = char
                i, char = next(data)
                if char != "'":    # Checking ending apostrophe
                    err("Missing apostrophe in input source.", 60)
                input_data["alphabet"].add(ident) # Adding symbol into set
                i, char = next(data)
                if char == ",":           # Next sybol is expected
                    pass
                elif char == "}":         # End of set
                    next_state     = 2    # Setting next state
                    expected_comma = True # Comma need to be inserted
                    state          = -1   # Switching to default state
                else:
                    err("Invalid input source", 60)

        elif state == 2: # State 2 represents loading rules
            if expected_brace_open: # Set of rules starts with {
                if char != "{":
                    err("Missing opening brace in input source.", 60)
                expected_brace_open = False
            elif char == "}":         # Set is empty
                next_state     = 3    # Setting next state
                expected_comma = True # Comma need to be inserted
                state          = -1   # Switching to default state
            else:
                # ident will now represents dictionary with 3 items:
                # starting state, read symbol and next state
                ident = {"start":str(), "symbol":str(), "next":str()}
                while char != "'":         # Loading starting state
                    ident["start"] += char
                    i, char = next(data)
                    if char is None:       # End of source was reached
                        err("Invalid imput source.", 60)
                if not pattern.match(ident["start"]): # Validing identificator
                    err("'%s' is invalid name of state."%(ident["start"]), 60)
                if not (ident["start"] in input_data["states"]): # Checking if state is declareted
                    err("State '%s' is not declareted in states."%(ident["start"]), 61)
                i, char = next(data) # Reading symbol
                if char == "'": # Symbol is ''
                    i, char = next(data)
                    if char != "'":
                        err("Missing apostrophe in input source.", 60)
                    ident["symbol"] = "''"
                else:           # Symbol is nothing special
                    ident["symbol"] = char
                if not(ident["symbol"] in input_data["alphabet"]): # Checking if symbol is declareted
                    err("Symbol '%s' is not declareted in input alphabet."%(ident["symbol"]), 61)
                i, char = next(data)
                if (char != "'"):  # Checking presence of ending apostrophe
                    err("Missing apostrophe in input source.", 60)
                i, char = next(data)
                if char != "-":    # Checking presence of ->
                    err("Invalid syntax in set of rules", 60)
                i, char = next(data)
                if char != ">":    # Checking presence of ->
                    err("Invalid syntax in set of rules", 60)
                i, char = next(data)
                while char != ",":             # Reading next state
                    if char is None:           # End of source was reached
                        err("Invalid input source.", 60)
                    elif char == "}":          # End of set was reached
                        next_state     = 3     # Setting next state
                        expected_comma = True  # Comma needs to be inserted
                        state          = -1    # Switching to current state
                        break
                    else:
                        ident["next"] += char
                        i, char = next(data)
                if not pattern.match(ident["next"]): # Validing state
                    err("'%s' is invalid name of state."%(ident["next"]), 60)
                if not(ident["next"] in input_data["states"]): # Checking if state is declareted
                    err("State '%s' is not declareted in states."%(ident["next"]), 61)
                if not(ident in input_data["rules"]): # Avoiding multiple rules declaration
                    input_data["rules"].append(ident)
        elif state == 3: # State 3 represents reading starting state
            ident = ""
            while char != ",": # Reading state identificator
                ident += char
                i, char = next(data)
                if char is None: # End of source reached
                    err("Invalid imput source.", 60)
            if not pattern.match(ident): # Validing identificator
                err("'%s' is invalid name of state."%(ident), 60)
            if not(ident in input_data["states"]): # Checking if state is declareted
                err("State '%s' is not declareted in states."%(ident), 61)
            input_data["start_state"] = ident # adding state
            state               = 4           # Switching to next state
            expected_brace_open = True        # Comma was read, brace is expected
        elif state == 4: # State 4 represents loading finishing states
            if expected_brace_open: # Reading starting brace of set
                if char != "{":
                    err("Missing opening brace in input source.", 60)
                expected_brace_open = False
            else:
                ident = ""
                while char != ",":                  # Reading state identificator
                    if char == "}":                 # End of set was reached
                        state                  = -1 # Switching to default state
                        expected_bracket_close = True # End of source expected
                        break
                    else:
                        ident  += char
                        i, char = next(data)
                        if char is None:
                            err("Invalid imput source.", 60)
                if not pattern.match(ident): # Validing state identificator
                    err("'%s' is invalid name of state."%(ident), 60)
                if not (ident in input_data["states"]): # Checking is state was declareted
                    err("Finishing state '%s' is not declareted in states."%(ident), 61)
                input_data["fin_states"].add(ident)
        elif state > 4: # states > 4 represents Error states
            err("Invalid input source.", 60)
        elif expected_comma: # Parsing comma between sets declaration
            if char != ",":
                err("Missing comma in input source.", 60)
            expected_comma = False
            state = next_state # Switching between states
            if state != 3: # State 3 does not represents sets and there is no brace
                expected_brace_open = True # Brace is expected
        elif expected_bracket_open: # Start of input source
            if char != "(":
                err("Missing opening bracked in input source.", 60)
            expected_brace_open   = True # Next character must be {
            expected_bracket_open = False
            state = 0 # Switching from default state into state 0
        elif expected_bracket_close: # End of inputsource
            if char != ")":
                err("Missing closing bracked in input source", 60)
            state = 5 # any other data will cause syntax error
    return input_data


del sys.argv[0]
args = Arguments(sys.argv)
if args.help:
    Arguments.print_help()
    exit(0)
input_data = parse_input(args)
debug(input_data)