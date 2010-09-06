import re
import time
import logging
import string
from NullHandler import NullHandler
import help
from template import template

"""
Reads in a Graphviz .dot file and generates a Verilog state machine based
on some simple rules.

1) State transitions should only be single transitions:
        state_name -> next_state_name;
        next_state_name -> next_next_state_name;
not
        state_name -> next_state_name -> next_next_state_name;

2) Events that cause state transitions are defined by .dot labels:
        state_name -> next_state_name [label = "start"];
    These events will generate input ports of the same name as the label.
"""
class StateTransition():
    def __init__(self, state, state_next, affector=None):
        self.state = state
        self.state_next = state_next
        self.affector = affector

class FSMGen():
    def __init__(self):
        self.__title = ""
        self.__unique_states = []
        self.__num_states = 0
        self.__transitions = []
        self.__unique_affectors = []
        self.logger = logging.getLogger("FSMGen")
        h = NullHandler()
        logging.getLogger("FSMGen").addHandler(h)

        self.subs = {   'filename':             "",
                        'creation_date':        "",
                        'title':                "",
                        'module_name':          "",
                        'inputs':               "",
                        'msb':                  "",
                        'lsb':                  "",
                        'state_params':         "",
                        'range':                "",
                        'next_state_logic':     "",
                        'state_generator':      "",
        }

    def getUniqueStates(self):
        return self.__unique_states

    def checkForDefaultState(self):
        """
        If the transition has an affector, check to see if there is
        also a same state transition with no affector.
        """
        self.logger.info("Checking for explicit same-state transitions")
        affector_states = []
        for t in self.__transitions:
            self.logger.debug("CHECKING: %s -> %s (%s)" % ( t.state,
                                                t.state_next,
                                                t.affector))
            if(t.affector is not None):
                # If it's already in affector_states don't bother putting
                # it in again
                if(t.state not in affector_states):
                    self.logger.debug("Adding state %s to the affector_states list" % t.state)
                    affector_states.append(t.state)

        for t in self.__transitions:
#            if((t.state == t.state_next) & (t.affector is None)):
            if(t.affector is None):
                if(t.state in affector_states):
                    # Remove that state from the list
                    if(affector_states.count(t.state) != 1):
                        raise FSMError("addSameStateTransition",
                            "Too many '%s' states in the transitions list" % t.state,
                            None)
                    else:
                        self.logger.debug("State %s already has a same-state transition" % t.state)
                        affector_states.remove(t.state)

        if(len(affector_states) > 0):
            raise MissingTransitionsError("addSameStateTransition",
                "Some states may not have all transitions covered",
                help.missing_transition_help,
                affector_states)

    def checkForDuplicateTransitions(self):
        """
        Takes a list of StateTransition objects and checks to see
        if there are any duplicate affectors that cause transitions
        from the same current state.  i.e.
            IDLE -> P1 [label='run'];
            IDLE -> P2 [label='run'];
        """
        self.logger.info("Checking for duplicate state transitions")

        state_trans = []
        for t in self.__transitions:
            # Make a string of the three values
            if(t.affector is not None):
                val = t.state + t.state_next + t.affector
            else:
                val = t.state + t.state_next

            if(val in state_trans):
                raise DuplicateTransitionError("checkForDuplicateTransitions",
                    "A duplicate state transition was found\n    %s -> %s" % (t.state, t.state_next),
                    None)
            else:
                state_trans.append(val)

        for i in state_trans:
            if(state_trans.count(i) > 1):
                print "More than once: %s" % i

        if(False):
            raise FSMError("Duplicate Affectors",
                "Attempting multiple state transitions with the same affector")

    def parseDotFile(self, filename):
        """
        The parser is looking for 3 things:
        1) FSM label
            label = "My Fancy State Machine"
        2) State transitions
            IDLE -> PIPE1;
        3) Explicit affectors which cause the state change
            IDLE -> PIPE1 [label = "rdy"];

        Checks:
            1) Same affector used to transition to multiple next states from
            the current state. i.e.
                    IDLE -> P1 [label='run'];
                    IDLE -> P2 [label='run'];
            2) No explicit same-state transition:
                    IDLE -> P1 [label='run'];
                but missing:
                    IDLE -> IDLE;
                The same-state transition will be created automatically.
        """
        re_fsm_name = re.compile(r'^\s*digraph\s*(\w+)')
        re_fsm_label = re.compile(r'^\s*label\s*=\s*\"(.*)\"')
        re_states = re.compile(r'^\s*(\w+)\s*->\s*(\w+)')
        re_affectors = re.compile(r'\[\s*label\s*=\s*\"(.*)\"\s*\]')

        f = open(filename, 'r')
        file = f.read()
        f.close()
        file = file.split('\n')
        for line in file:
            st = None

                ## Find FSM Module Name
            m = re_fsm_name.search(line)
            if(m is not None):
                self.__name = m.group(1)
                self.logger.info("Found Module Name: %s" % self.__name)

                ## Find FSM Title
            m = re_fsm_label.search(line)
            if(m is not None):
                self.__title = m.group(1)
                self.logger.info("Found Title: %s" % self.__title)

                ## Find States and Next States
            m_state = re_states.search(line)
            if(m_state is not None):
                state = m_state.group(1)
                if state not in self.__unique_states:
                    self.__unique_states.append(state)
                    ## Find Transitions
                m_affector = re_affectors.search(line)
                if(m_affector is not None):
                    affector = m_affector.group(1)
                    ## Strip off ~ and !
                    affector_stripped = re.sub(r'~|!','', affector)
                    if(affector_stripped not in self.__unique_affectors):
                        self.logger.debug("Adding unique affector '%s'" % affector_stripped)
                        self.__unique_affectors.append(affector_stripped)
                else:
                    affector = None

                self.__transitions.append(StateTransition(m_state.group(1),
                                                        m_state.group(2),
                                                        affector))
            self.__num_states = len(self.__unique_states)

    def getInputPorts(self):
        """
        Creates and returns a string of input ports.
        """
        pass

    def getOutputPorts(self):
        """
        Creates and returns a string of output ports.
        """
        pass

    def writeVerilog(self):
        self.subs['filename'] = self.__name + '.v'
        s = string.Template(template)
        f = open(self.subs['filename'], 'w')

        self.subs['creation_date'] = time.strftime("%b %d %Y")
        self.subs['title'] = self.__title
        self.subs['module_name'] = self.__name
        for i in self.__unique_affectors:
            self.subs['inputs'] += "    input   wire %s,\n" % i
        self.subs['msb'] = self.__num_states-1
        self.subs['lsb'] = 0
        for i in range(self.__num_states):
            str = "    %s = %d" % (self.__unique_states[i], i)
            if(i < self.__num_states-1):
                str += ",\n"
            else:
                str += ";"
            self.subs['state_params'] += str
        self.subs['range'] = self.__num_states

        f.write(s.safe_substitute(self.subs))
        f.close()

class FSMError(Exception):
    def __init__(self, method_name, error_message, long_message):
        Exception.__init__(self)
        self.method_name = method_name
        self.error_message = error_message
        self.long_message = long_message

class MissingTransitionsError(FSMError):
    def __init__(self, method_name, error_message, long_message, states):
        FSMError.__init__(self, method_name, error_message, long_message)
        self.states = states

class DuplicateTransitionError(FSMError):
    def __init__(self, method_name, error_message, long_message):
        FSMError.__init__(self, method_name, error_message, long_message)
