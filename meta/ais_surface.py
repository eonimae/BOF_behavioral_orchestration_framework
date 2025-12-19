# ais_surface.py
# Adaptive Intent States (AIS) - Interaction Surface

class AISurface:
    """
    Manages adaptive intent states and interaction context.
    Acts as the cognitive layer that interprets user intent
    and passes it to the execution layer.
    """

    def __init__(self):
        # Possible states: Focus, Ambiguity, Execution, Reflection
        self.current_state = "neutral"
        self.state_transitions = {
            "neutral": ["Focus"],
            "Focus": ["Ambiguity", "Execution"],
            "Ambiguity": ["Focus", "Reflection"],
            "Execution": ["Reflection"],
            "Reflection": ["Focus"]
        }

    def update_state(self, new_state):
        """
        Update the current adaptive intent state
        if the transition is valid.
        """
        if new_state in self.state_transitions.get(self.current_state, []):
            print(f"[AIS] State transition: {self.current_state} -> {new_state}")
            self.current_state = new_state
        else:
            print(f"[AIS] Invalid transition: {self.current_state} -> {new_state}")

    def interpret(self, signal):
        """
        Interpret external or internal signals to adjust state.
        Example: a vague or conflicting signal may induce 'Ambiguity',
        a clear signal may reinforce 'Focus'.
        """
        print(f"[AIS] Interpreting signal: {signal}")
        if "?" in signal or "maybe" in signal.lower():
            self.update_state("Ambiguity")
        else:
            self.update_state("Focus")
        return f"Interpreted({signal})"

    def emit_state(self, state_name=None):
        """
        Emit the current cognitive state or a requested one.
        This represents AIS broadcasting its condition
        to the orchestrator for context-aware decisions.
        """
        state_to_emit = state_name if state_name else self.current_state
        print(f"[AIS] Cognitive State -> {state_to_emit}")
        return state_to_emit

