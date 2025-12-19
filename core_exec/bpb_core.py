# bpb_core.py
# Behavioral Protocol Blueprint (BPB)

from data.log.logger import BOFLogger

class BPBCore:
    """
    Core engine for the Behavioral Protocol Blueprint.
    Defines the behavioral cycle (L1–L5) and links to methodologies.
    """

    def __init__(self):
        self.state = "idle"
        self.history = []
        self.logger = BOFLogger()  # Initialize logger instance

    def step_L1(self, input_data):
        """L1: Input validation."""
        self.history.append(("L1", input_data))
        msg = "[BPB] L1 validation step complete."
        print(msg)
        self.logger.write(msg)

    def step_L2(self, context):
        """L2: Contextual iteration."""
        self.history.append(("L2", context))
        msg = "[BPB] L2 iteration step complete."
        print(msg)
        self.logger.write(msg)

    def step_L3(self, evaluation):
        """L3: Evaluation phase."""
        self.history.append(("L3", evaluation))
        msg = "[BPB] L3 evaluation step complete."
        print(msg)
        self.logger.write(msg)

    def step_L4(self, feedback):
        """L4: Feedback synthesis."""
        self.history.append(("L4", feedback))
        msg = "[BPB] L4 feedback step complete."
        print(msg)
        self.logger.write(msg)

    def step_L5(self, calibration):
        """L5: Calibration and learning."""
        self.history.append(("L5", calibration))
        msg = "[BPB] L5 calibration step complete."
        print(msg)
        self.logger.write(msg)

    def run_cycle(self, data):
        """Executes all five layers sequentially."""
        self.logger.section("BPB Behavioral Cycle Start")
        print("[BPB] Starting behavioral cycle...")
        self.logger.write("[BPB] Starting behavioral cycle...")

        self.step_L1(data)
        self.step_L2(data)
        self.step_L3(data)
        self.step_L4(data)
        self.step_L5(data)

        print("[BPB] Behavioral cycle complete.")
        self.logger.write("[BPB] Behavioral cycle complete.")
        self.logger.section("BPB Behavioral Cycle End")

    # --- Optional Skill Integration Layer (non-invasive) ---
    def run_skill(self, skill_name, input_text, skill_executor=None):
        """
        Invokes an external skill module (e.g., WritingSkill) without affecting
        the internal L1–L5 behavioral cycle.
        """
        print(f"[BPB] Activating external skill: {skill_name}")
        self.logger.section(f"BPB Skill Activation: {skill_name}")

        result = None
        try:
            if callable(skill_executor):
                # Hook: external registry/executor handles the skill
                result = skill_executor(skill_name, input_text)
            elif skill_name.lower() == "writing":
                from core_exec.skills.writing import WritingSkill, skill_writing
                # Prefer function hook for future tool exposure
                try:
                    _ = skill_writing  # noqa: F401
                    result = skill_writing(input_text)
                except Exception:
                    skill = WritingSkill()
                    result = skill.run(input_text)
            elif skill_name.lower() == "reading":
                from core_exec.skills.reading import ReadingSkill, skill_reading
                try:
                    _ = skill_reading  # noqa: F401
                    result = skill_reading(input_text)
                except Exception:
                    skill = ReadingSkill()
                    result = skill.run(input_text)
            else:
                msg = f"[BPB] Skill '{skill_name}' not found."
                print(msg)
                self.logger.write(msg)

        except Exception as e:
            msg = f"[BPB] Error activating skill '{skill_name}': {e}"
            print(msg)
            self.logger.write(msg)

        self.logger.section(f"BPB Skill Termination: {skill_name}")
        return result

