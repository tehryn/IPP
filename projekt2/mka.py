#!/usr/bin/env python3.5
import sys
import re
def debug(*args):
    print("-----------")
    for arg in args:
        sys.stdout.write(str(arg) + "\n")
        print("- - - - - -")
    print("-----------")


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

class FiniteStateMachine:
    states     = set()
    alphabet   = set()
    rules      = list()
    start      = str()
    fin_states = set()

    reachable_states       = set()
    unreachable_states     = set()
    finishing_states       = set()
    non_finishing_states   = set()
    nondeterministic_rules = list()
    epsilon_rules          = list()


    def __init__(self, declaration):
        self.count = 0
        self.states           = declaration["states"]
        self.alphabet         = declaration["alphabet"]
        self.rules            = declaration["rules"]
        self.start            = declaration["start_state"]
        self.fin_states       = declaration["fin_states"]
        self.finishing_states = self.fin_states.copy()

        self.__set_reachable(self.start)
        self.unreachable_states   = self.states.difference(self.reachable_states)
        if self.unreachable_states:
            tmp = FiniteStateMachine.states_to_string(self.unreachable_states)
            err("State(s) %s are not reachable."%(tmp), 62)
        self.__set_non_finishing()
        if len(self.non_finishing_states) > 1:
            tmp = FiniteStateMachine.states_to_string(self.non_finishing_states)
            err("States %s are non finishing."%(tmp), 62)
        self.__find_nondeterminism()
        if self.nondeterministic_rules:
            tmp = FiniteStateMachine.rules_to_string(self.nondeterministic_rules)
            err("Rules:\n%s\nare non deterministic."%(tmp), 62)
        self.__set_epsilon()
        if self.epsilon_rules:
            tmp = FiniteStateMachine.rules_to_string(self.epsilon_rules)
            err("Rules:\n%s\nare epsilon rules."%(tmp), 62)


    def __str__(self):
        out = "(\n"
        out += FiniteStateMachine.states_to_string(self.states) + ",\n"
        out += FiniteStateMachine.alphabet_to_string(self.alphabet) + ",\n"
        out += FiniteStateMachine.rules_to_string(self.rules) + ",\n"
        out += self.start + ",\n"
        out += FiniteStateMachine.states_to_string(self.fin_states) + "\n)\n"
        return out


    def __set_reachable(self, start_state):
        self.reachable_states.add(start_state)
        for rule in self.rules:
            if not (rule["next"] in self.reachable_states) and rule["start"] == start_state:
                self.__set_reachable(rule["next"])


    def __set_non_finishing(self):
        tmp = True
        while tmp:
            tmp = False
            for rule in self.rules:
                if rule["next"] in self.finishing_states and not(rule["start"] in self.finishing_states):
                    self.finishing_states.add(rule["start"])
                    tmp = True
        self.non_finishing_states = self.states.difference(self.finishing_states)


    def __find_nondeterminism(self):
        for rule in self.rules:
            for cmp in self.rules:
                if cmp["start"] == rule["start"] and cmp["symbol"] == rule["symbol"]:
                    if cmp != rule:
                        self.nondeterministic_rules.append(rule)


    def __set_epsilon(self):
        for rule in self.rules:
            if rule["symbol"] == "epsilon":
                self.epsilon_rules.append(rule)


    def minimize(self):
        def split(X, d):
            X1 = set()
            X2 = set()
            next_states = set()
            next_of_current = set()
            for state in X:
                if not X1:
                    X1.add(state)
                    next_states = {r["next"] for r in self.rules if r["start"] == state and r["symbol"] == d}
                else:
                    next_of_current = {r["next"] for r in self.rules if r["start"] == state and r["symbol"] == d}
                    if next_of_current <= next_states:
                        X1.add(state)
                    else:
                        X2.add(state)
            return [X1, X2]

        def parse_new_rule(states, symbol, next):
            new_state = str()
            new_next  = str()
            isStart   = False
            isFin     = False
            for state in sorted(list(states)):
                new_state += state + "_"
                if state == self.start:
                    isStart = True
                if state in self.fin_states:
                    isFin = True
            for state in sorted(list(next)):
                new_next += state + "_"
            new_state = new_state[:-1]
            new_next  = new_next[:-1]
            new_rule  = {"start":new_state, "symbol":symbol,"next":new_next,
                         "start_state":isStart, "fin_state":isFin}
            return new_rule


        Qm = list()
        if (self.fin_states):
            Qm.append(self.fin_states)
        if (self.states.difference(self.fin_states)):
            Qm.append(self.states.difference(self.fin_states))
        condition   = True
        next_states = set()
        new_rules   = list()
        while condition:
            condition = False
            new_rules   = list()
            for X in Qm:
                for d in self.alphabet:
                    next_states = {r["next"] for r in self.rules if d == r["symbol"] and r["start"] in X }
                    found = False
                    for Qi in Qm:
                        if next_states.issubset(Qi):
                            found = True
                            new_rules.append(parse_new_rule(X, d, Qi))
                    if not found:
                        condition = True
                        X12 = split(X, d)
                        del Qm[Qm.index(X)]
                        Qm.append(X12[0])
                        Qm.append(X12[1])
                        break
                if not found:
                    break

        self.states = {r["start"] : r["next"] for r in new_rules}
        self.rules  = new_rules
        self.start  = [r["start"] for r in new_rules if r["start_state"] is True][0]
        self.fin_states = {r["start"] for r in new_rules if r["fin_state"] is True}
        return self

    def rules_to_string(rules):
        output = "{"
        for rule in rules:
            if rule["symbol"] == "epsilon":
                rule["symbol"] = ""
        rules.sort(key = lambda r:(r["start"], r["symbol"]))
        for rule in rules:
            output += "\n" + rule["start"] + " '" + rule["symbol"] + "'" + " -> "
            output += rule["next"] + ","
        output = output[:-1] + "\n}"
        return output


    def states_to_string(states):
        out = "{"
        for state in sorted(list(states)):
            out += state + ", "
        out = out[:-2] + "}"
        return out

    def alphabet_to_string(alphabet):
        out = "{"
        for d in sorted(list(alphabet)):
            out += "'" + d + "'" + ", "
        out = out[:-2] + "}"
        return out



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
    pattern                = re.compile(r"[_]{0}[aA-zZ]+\w*[_]{0}")

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
            elif char == "}":
                expected_comma = True # Comma need to be inserted
                state          = -1   # Switching to default state
                next_state     = 1    # Setting next state
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
                regex = pattern.match(ident)
                if not regex or regex.group(0) != ident:  # Testing validity of identificator
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
                if char != "'":  # 1st apostrophe
                    err("Missing apostrophe in input source.", 60)
                i, char = next(data)
                if (char == "'"):     # 2nd apostrophe
                    i, char = next(data)
                    if (char != "'"): # 3rd apostrophe
                        if char != "," and char != "}":
                            err("Invalid member of alphabet.", 60)
                        else:
                            ident = "epsilon"
                            input_data["alphabet"].add(ident)
                    else:
                        ident = "''"
                elif char is None: # End of source is reached
                    err("Invalid input source.", 60)
                else:              # Char is nothing special
                    ident = char
                if ident != "epsilon":
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
                regex = pattern.match(ident["start"])
                if not regex or regex.group(0) != ident["start"]: # Validing identificator
                    err("'%s' is invalid name of state."%(ident["start"]), 60)
                if not (ident["start"] in input_data["states"]): # Checking if state is declareted
                    err("State '%s' is not declareted in states."%(ident["start"]), 61)
                i, char = next(data) # Reading symbol
                if char == "'": # 2nd apostrophe
                    i, char = next(data)
                    if char != "'": # 3rd apostrophe
                        if char != "-":
                            err("Missing apostrophe in input source.", 60)
                        else:
                            ident["symbol"] = "epsilon"
                    else:
                        ident["symbol"] = "''"
                else:           # Symbol is nothing special
                    ident["symbol"] = char
                if not(ident["symbol"] in input_data["alphabet"]): # Checking if symbol is declareted
                    err("Symbol '%s' is not declareted in input alphabet."%(ident["symbol"]), 61)
                if ident["symbol"] != "epsilon":
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
                regex = pattern.match(ident["next"])
                if not regex or regex.group(0) != ident["next"]: # Validing state
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
            regex = pattern.match(ident)
            if not regex or regex.group(0) != ident: # Validing identificator
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
            elif char == "}":                       # set is emty
                state                  = -1         # Switching to default state
                expected_bracket_close = True       # End of source expected
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
                regex = pattern.match(ident)
                if not regex or regex.group(0) != ident: # Validing state identificator
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


def write(args, finte_state_machine):
    try:
        if args.output == sys.stdout:
            file = sys.stdout
        else:
            file = open(args.output, "w")
    except:
        err("Unable to open output file '%s'"%(args.output), 3)
    if args.finish:
        if finte_state_machine.non_finishing_states:
            file.write(str(list(finte_state_machine.non_finishing_states)[0]))
        else:
            file.write(str(0))
        exit(0)
    if args.minimize:
        file.write(str(finite_state_machine.minimize()))
    else:
        file.write(str(finite_state_machine))
    file.close()

del sys.argv[0]                     # Deletes program name from arguments
args = Arguments(sys.argv)          # Parse arguments
if args.help:                       # Prints help if needed
    Arguments.print_help()
    exit(0)
finite_state_machine = parse_input(args)   # Opens, closes and parses input source
finite_state_machine = FiniteStateMachine(finite_state_machine) # Creates Finite state machine
write(args, finite_state_machine)