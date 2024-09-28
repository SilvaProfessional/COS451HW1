import sys
from io import StringIO


# Automata are defined by the following lines
#   -> fsa (What happens when not reading an automata if not given fsa)
#   -> name (only the first token in the line is taken and rest is thrown out)
#   -> alphabet (list of tokens)
#   -> states in form {state_name transition1 transition2 ...} (no {}, that's just for formatting here)
#       -> what happens if too many or too little transitions are given
class Automaton:
    def __init__(self, name, alphabet, state_table, accept_states):
        # ASSUMES NAME HAS NO NEWLINE ATTACHED
        self.name = name # string
        self.alphabet = alphabet # list of characters
        self.state_table = state_table # list of ntuples with state_name, trans1, trans2, ... where n = len(alphabet)+1
        self.accept_states = accept_states # list of state_names

    def __str__(self):
        retval = ""
        retval += self.name
        retval += "\n"

        retval += "  "

        for i in range(len(self.alphabet)):
            for j in range(len(self.state_table[0][0])):
                retval += " "
            retval += self.alphabet[i]

        retval += "\n"

        for state in self.state_table:
            if state[0] in self.accept_states:
                retval += "*"
            else:
                retval += " "
            for token in state:
                retval += token + " "
            retval += '\n'

        return retval

    def check_accept(self, input_string):

        current_state = self.state_table[0]

        for char in input_string:
            if char not in self.alphabet:
                sys.stderr.write("Provided transition not of the automatons alphabet, ending execution")
                return None
            transition_index = self.alphabet.index(char) + 1

            next_state = current_state[transition_index]

            for state in self.state_table:
                if state[0] == next_state:
                    current_state = state
                    break

        final_state_name = current_state[0]
        return final_state_name in self.accept_states


# Program needs to be able to store and use literals, mapping a name to a definition
#   -> maps to a string, automata, or other literal's definition (not sure this was true but its implemented so whatever)
#       -> when mapping to an automaton, use fsa as the definition, then immediately define the automaton
#   -> Literals come in form (name, definition)
# This may need other functions, so I'll leave it as its own object rather than a list in main
class LiteralHandler:
    def __init__(self):
        self.literals = []

    def get_value(self, literal_name):
        for literal in self.literals:
            if literal_name == literal[0]:
                return literal[1]
        return None


# Can alphabet be empty?
# Can state table be empty?
# can accept_states be empty???
def check_valid_automaton(name, alphabet, state_table, accept_states):

    if len(alphabet) == 0:
        print("alphabet cannot be empty", file=sys.stderr)
        return None

    if len(state_table) == 0:
        print("automaton cannot be defined with 0 states", file=sys.stderr)
        return None

    if len(accept_states) == 0:
        print("automaton cannot be defined with 0 accept states", file=sys.stderr)
        return None

    if len(accept_states) > len(state_table):
        print("more accept states than defined states", file=sys.stderr)
        return None

    for state in state_table:
        if len(state) < len(alphabet) + 1:
            print("state \"" + state[0] + "\" in state table is missing one or more transitions", file=sys.stderr)
            return None
        elif len(state) > len(alphabet) + 1:
            print("state \"" + state[0] + "\" in state table has one or more too many transitions", file=sys.stderr)
            return None

    return Automaton(name, alphabet, state_table, accept_states)


# Breaks if newline which marks end of automata definition has any whitespace (not anymore)
# Expects fsa definition to be terminated with a "\n\n" (blank line after state table)
# probably shouldn't read from stdin directly to maintain cohesion with other functions
#   -> definitely needs to be reworked to work line by line :/
# Breaks if there is white space after *
def get_automaton_from_text_block(input_string):

    retval_name = ""
    retval_alph = []
    retval_state_table = []
    retval_accept_states = []

    text_block = StringIO(input_string)

    for line in text_block.readlines():
        if retval_name == "":
            retval_name = line.split()[0]
        elif len(retval_alph) == 0:
            for char in line.split():
                retval_alph.append(char)
        else:
            if line[0] == "\n":
                return check_valid_automaton(retval_name, retval_alph, retval_state_table, retval_accept_states)

            tokens = line.split()
            if tokens[0][0] == '*':
                tokens[0] = tokens[0][1:]
                retval_accept_states.append(tokens[0])
            retval_state_table.append(tokens)

# Program needs to be able to parse the following keywords
#   -> quit
#   -> print
#   -> define
#   -> run
# Quit will be handled in the main loop, to make EOF easier to handle, all other executions will be passed to a function


# deprecated
def exec_print(literal_handler, literal_name):
    for literal in literal_handler.literals:
        if literal_name == literal[0]:
            sys.stdout.write(str(literal[1]) + '\n')
            return


def exec_define(literal_handler, literal_name, literal_val):
    for i in range(len(literal_handler.literals)):
        if literal_name == literal_handler.literals[i][0]:
            literal_handler.literals[i] = (literal_name, literal_val)
            return
    literal_handler.literals.append((literal_name, literal_val))


def exec_run(literal_handler, literal_name, run_value):
    automaton = literal_handler.get_value(literal_name)
    if automaton is not None:
        check_value = automaton.check_accept(run_value)

        if check_value is None:
            pass
        elif check_value is True:
            sys.stdout.write("accept\n")
        elif check_value is False:
            sys.stdout.write("reject\n")


# How do we handle whitespaces in strings, are they even allowed? They don't make sense
# I'm removing them
# Breaks if there are multiple strings
def clean_line_with_string(line):
    line_tokens = line.split("\"")

    if len(line_tokens) != 3:
        sys.stderr.write("Instruction contains invalid number of strings")
        return None

    string = line_tokens[1]
    string_tokens = string.split()

    string_cleaned = ""
    for string_token in string_tokens:
        string_cleaned += string_token

    line_cleaned = ""
    line_tokens[1] = string_cleaned
    for line_token in line_tokens:
        line_cleaned += line_token

    return line_cleaned


# Main loop takes lines (strings of tokens; from stdin) of user input until quit token is found
#   -> Tokens are delimited by spaces or tabs
#   -> lines are terminated by a single newline char (at least during fsa definition, but not during execution?)

# Main loop reads stdin line by line and sends off to specific functions for execution of specific verbs
# What does main do if it comes across an unexpected input?
if __name__ == '__main__':
    lh = LiteralHandler()
    building_automaton = False
    automaton_definition_text_block = ""
    current_automaton_name = ""
    string_flag = False

    while True:
        line = sys.stdin.readline()

        # EOF
        if len(line) == 0:
            sys.exit()

        if line[0] == '\n' and building_automaton:
            automaton_definition_text_block += '\n'
            exec_define(lh, current_automaton_name, get_automaton_from_text_block(automaton_definition_text_block))
            current_automaton_name = ""
            automaton_definition_text_block = ""
            building_automaton = False
            continue

        if line.find("\"") != -1:
            line = clean_line_with_string(line)
            if line is None:
                continue
            string_flag = True

        tokens = line.split()
        if len(tokens) == 0:
            continue

        if building_automaton:
            automaton_definition_text_block += line
            continue

        if tokens[0] == "quit":
            sys.exit()
        elif tokens[0] == "print":
            val = lh.get_value(tokens[1])
            if val is not None:
                sys.stdout.write(str(val) + "\n")

        elif tokens[0] == "define":
            if tokens[2] == "fsa":
                building_automaton = True
                current_automaton_name = tokens[1]
                continue

            if string_flag:
                exec_define(lh, tokens[1], tokens[2])
                string_flag = False
            else:
                exec_define(lh, tokens[1], lh.get_value(tokens[2]))

        elif tokens[0] == "run":

            if lh.get_value(tokens[1]) is None:
                sys.stderr.write("Provided automaton is undefined")
                continue

            if string_flag:
                exec_run(lh, tokens[1], tokens[2])
                string_flag = False
            else:
                execute_string = lh.get_value(tokens[2])
                if execute_string is None:
                    sys.stderr.write("Provided literal is undefined")
                    continue
                exec_run(lh, tokens[1], execute_string)

        else:
            print("Invalid instruction")

