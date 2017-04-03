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
            Print both private and public variables with its values
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
    try:
        input = args.input
        if (not (input is sys.stdin)):
            input = open(args.input, "r")
        data = input.read()
        input.close()
    except:
        err("Unable to open input file '" + str(args.input) + "' for reading", 2)
    if args.insensitive:
        data = data.lower()
    data = prepare_data(data)
    data = retrieve_data(data)
    return data

def prepare_data(data):
    comment     = False
    apostrophe  = False
    raw_string = str()
    for c in data:
        if comment:
            if c == "\n":
                comment = False
            continue
        elif not apostrophe and c == "#":
            comment = True
            continue
        elif c == "'":
            if not apostrophe:
                apostrophe = True
            else:
                apostrophe = False
        if(not c.isspace() or (c.isspace() and apostrophe)):
            raw_string += c
    return raw_string


def retrieve_data(data):
    input_data             = {"states":set(), "alphabet":set(), "rules":list(),
                              "start_state":str(), "fin_states":set()}
    ident                  = str()
    pattern                = re.compile(r"[_]{0}[aA-zZ]\w*[_]{0}")
    state                  = -1
    next_state             = 0
    expected_bracket_open  = True
    expected_bracket_close = False
    expected_brace_open    = False
    expected_brace_close   = False
    expected_comma         = False
    expected_apostrophe    = False
    expected_arrow         = False
    data = enumerate(data)
    for i, char in data:
        if state == 0:
            if expected_brace_open:
                if char != "{":
                    err("Missing opening brace in input source.", 60)
                expected_brace_open = False
            else:
                ident = ""
                while char != ",":
                    if char == "}":
                        expected_comma = True
                        state          = -1
                        next_state     = 1
                        break
                    else:
                        ident += char
                        i, char = next(data)
                        if char == None:
                            err("Invalid imput source.", 60)
                if not pattern.match(ident):
                    err("'%s' is invalid name of state."%(ident), 60)
                input_data["states"].add(ident)
        elif state == 1:
            if expected_brace_open:
                if char != "{":
                    err("Missing opening brace in input source.", 60)
                expected_brace_open = False
            elif char == "}":
                next_state     = 2
                state          = -1
                expected_comma = True
            else:
                if char != "'":
                    err("Missing apostrophe in input source.", 60)
                i, char = next(data)
                if (char == "'"):
                    i, char = next(data)
                    if (char != "'"):
                        err("Invalid member of alphabet.", 60)
                    ident = "''"
                elif (char == None):
                    err("Invalid input source.", 60)
                else:
                    ident = char
                i, char = next(data)
                if char != "'":
                    err("Missing apostrophe in input source.", 60)
                input_data["alphabet"].add(ident)
                i, char = next(data)
                if char == ",":
                    pass
                elif char == "}":
                    next_state     = 2
                    expected_comma = True
                    state          = -1
                else:
                    err("Invalid input source", 60)

        elif state == 2:
            if expected_brace_open:
                if char != "{":
                    err("Missing opening brace in input source.", 60)
                expected_brace_open = False
            elif char == "}":
                next_state     = 3
                expected_comma = True
                state          = -1
            else:
                ident = {"start":str(), "symbol":str(), "next":str()}
                while char != "'":
                    ident["start"] += char
                    i, char = next(data)
                    if char == None:
                        err("Invalid imput source.", 60)
                if not pattern.match(ident["start"]):
                    err("'%s' is invalid name of state."%(ident["start"]), 60)
                if not (ident["start"] in input_data["states"]):
                    err("State '%s' is not declareted in states."%(ident["start"]), 61)
                i, char = next(data)
                if char == "'":
                    i, char = next(data)
                    if char != "'":
                        err("Missing apostrophe in input source.", 60)
                    ident["symbol"] = "''"
                else:
                    ident["symbol"] = char
                if not(ident["symbol"] in input_data["alphabet"]):
                    err("Symbol '%s' is not declareted in input alphabet."%(ident["symbol"]), 61)
                i, char = next(data)
                if (char != "'"):
                    err("Missing apostrophe in input source.", 60)
                i, char = next(data)
                if char != "-":
                    err("Invalid syntax in set of rules", 60)
                i, char = next(data)
                if char != ">":
                    err("Invalid syntax in set of rules", 60)
                i, char = next(data)
                while char != ",":
                    if char == None:
                        err("Invalid input source.", 60)
                    elif char == "}":
                        next_state     = 3
                        expected_comma = True
                        state          = -1
                        break
                    else:
                        ident["next"] += char
                        i, char = next(data)
                if not pattern.match(ident["next"]):
                    err("'%s' is invalid name of state."%(ident["next"]), 60)
                if not(ident["next"] in input_data["states"]):
                    err("State '%s' is not declareted in states."%(ident["next"]), 61)
                if not(ident in input_data["rules"]):
                    input_data["rules"].append(ident)
        elif state == 3:
            ident = ""
            while char != ",":
                ident += char
                i, char = next(data)
                if char == None:
                    err("Invalid imput source.", 60)
            if not pattern.match(ident):
                err("'%s' is invalid name of state."%(ident), 60)
            if not(ident in input_data["states"]):
                err("State '%s' is not declareted in states."%(ident), 61)
            input_data["start_state"] = ident
            state               = 4
            expected_brace_open = True
        elif state == 4:
            if expected_brace_open:
                if char != "{":
                    err("Missing opening brace in input source.", 60)
                expected_brace_open = False
            else:
                ident = ""
                while char != ",":
                    if char == "}":
                        expected_comma         = False
                        state                  = -1
                        expected_bracket_close = True
                        break
                    else:
                        ident  += char
                        i, char = next(data)
                        if char == None:
                            err("Invalid imput source.", 60)
                if not pattern.match(ident):
                    err("'%s' is invalid name of state."%(ident), 60)
                input_data["fin_states"].add(ident)
        elif state > 4:
            err("Invalid input source.", 60)
        elif expected_comma:
            if char != ",":
                err("Missing comma in input source.", 60)
            expected_comma = False
            state = next_state
            if state != 3:
                expected_brace_open = True
        elif expected_bracket_open:
            if char != "(":
                err("Missing opening bracked in input source.", 60)
            expected_brace_open   = True
            expected_bracket_open = False
            state = 0
        elif expected_bracket_close:
            if char != ")":
                err("Missing closing bracked in input source", 60)
            state = 5
    return input_data


del sys.argv[0]
args = Arguments(sys.argv)
if args.help:
    Arguments.print_help()
    exit(0)
input_data = parse_input(args)
debug(input_data)