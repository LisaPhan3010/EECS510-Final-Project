# automaton.py
class Automaton:
    def __init__(self, states, inputs, start_state, accept_states, transitions):
        #initialize the automaton
        self.states = states
        self.inputs = inputs
        self.start_state = start_state
        self.accept_states = accept_states
        self.transitions = transitions

    #add a transition from one state to another state with input symbol
    def add_transition(self, from_state, symbol, to_state):
        if (from_state, symbol) not in self.transitions:
            self.transitions[(from_state, symbol)] = set()
        self.transitions[(from_state, symbol)].add(to_state)

    #check if the automaton accepts the given string
    def accepts(self, input_string):
        symbols = input_string.split()
        current_states = {self.start_state}
        path = [(self.start_state, '')]
        for symbol in symbols:
            next_states = set()
            for state in current_states:
                if (state, symbol) in self.transitions: 
                    next_states.update(self.transitions[(state, symbol)]) 
                    path.append((state, symbol))
                current_states = next_states
                if not current_states:
                    return 'reject'
        for state in current_states:
            if state in self.accept_states:
                return 'accept', path
        return 'reject'
    
    