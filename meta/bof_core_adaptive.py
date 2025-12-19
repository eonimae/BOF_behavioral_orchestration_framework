# bof_core_adaptive.py
# Behavioral Orchestration Framework (BOF) – Adaptive Core
# Extension of BOFCore for cognitive orchestration and dynamic routing

from datetime import datetime
import json
from pathlib import Path

class EventBus:
    """
    Internal channel for signals between AISurface, ACFAdapter, and BPBCore.
    Collects InputEvents, InternalStateEvents, ToolEvents, and ConsentEvents.
    """
    def __init__(self, persist_path=None):
        self.events = []
        self.persist_path = Path(persist_path) if persist_path else None
        if self.persist_path and self.persist_path.exists():
            try:
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            self.events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"[EventBus] Warning: could not load persisted events: {e}")

    def publish(self, event_type, payload):
        timestamp = datetime.now().isoformat()
        event = {"time": timestamp, "type": event_type, "data": payload}
        self.events.append(event)
        if self.persist_path:
            try:
                self.persist_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.persist_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event) + "\n")
            except Exception as e:
                print(f"[EventBus] Warning: failed to persist event: {e}")

    def fetch_latest(self, event_type=None):
        if not event_type:
            return self.events[-1] if self.events else None
        filtered = [e for e in self.events if e["type"] == event_type]
        return filtered[-1] if filtered else None


class PolicyGate:
    """
    Reads Model Spec and context policies before any transition or skill execution.
    Ensures all actions remain within truthfulness, safety, and behavioral bounds.
    """
    def __init__(self, active_policies=None, external_checker=None):
        base = {
            "allow": {"*": True},  # wildcard allow by default
            "deny": set()
        }
        self.active_policies = {
            "allow": dict(base["allow"]),
            "deny": set(base["deny"])
        }
        if active_policies:
            allow_cfg = active_policies.get("allow", {})
            deny_cfg = active_policies.get("deny", set())
            self.active_policies["allow"].update(allow_cfg)
            self.active_policies["deny"].update(deny_cfg)
        # Optional callable: (action:str, context:dict)->bool
        self.external_checker = external_checker

    def check(self, action, context=None):
        # Hook: delegate to external checker if provided
        context = context or {}
        print(f"[PolicyGate] Checking policy for action: {action}")

        # Local deny takes precedence
        if action in self.active_policies["deny"]:
            print("[PolicyGate] Decision: DENY (deny-list)")
            return False

        allow_map = self.active_policies["allow"]
        wildcard = allow_map.get("*", True)
        decision = wildcard
        reason = "wildcard-allow" if wildcard else "explicit-required"

        if not wildcard:
            decision = allow_map.get(action, False)
            reason = "explicit-allow" if decision else "not-allowed"
        else:
            if action in allow_map:
                decision = allow_map[action]
                reason = "explicit-override"

        if not decision:
            print(f"[PolicyGate] Decision: DENY ({reason})")
            return False

        if self.external_checker:
            try:
                external_decision = bool(self.external_checker(action, context))
                if not external_decision:
                    print("[PolicyGate] Decision: DENY (external checker)")
                    return False
                reason = f"{reason}+external"
            except Exception as e:
                print(f"[PolicyGate] External checker error: {e}")

        print(f"[PolicyGate] Decision: ALLOW ({reason})")
        return True


class RouterHybrid:
    """
    Combines AIS state, ACF directives, and detected intent to select the proper route or skill.
    """
    def __init__(self):
        self.current_skill = None

    def decide(self, intent, ais_state, acf_mode, modes=None, context=None):
        print(f"[Router] Deciding route for intent={intent}, state={ais_state}, mode={acf_mode}, modes={modes}")
        selected = "writing"
        reason = "fallback"

        writing_indicators = {"writing", "creative", "story", "composition"}
        reading_indicators = {"reading", "analysis", "review", "study", "summary"}
        research_indicators = {"research", "search", "analysis"}

        intent_lower = (intent or "").lower()
        if any(token in intent_lower for token in reading_indicators):
            selected = "reading"
            reason = "intent-reading"
        elif any(token in intent_lower for token in writing_indicators):
            selected = "writing"
            reason = "intent-writing"

        if modes and reason == "fallback":
            lowered = {m.lower() for m in modes}
            if lowered & writing_indicators:
                selected = "writing"
                reason = "mode-writing"
            elif lowered & reading_indicators:
                selected = "reading"
                reason = "mode-reading"
            elif lowered & research_indicators:
                selected = "reading"
                reason = "mode-analysis"

        if context:
            requested = context.get("requested_skill")
            if requested:
                selected = requested
                reason = "context-request"

        self.current_skill = selected
        print(f"[Router] Route decision: {selected} ({reason})")
        return selected


class BOFCoreAdaptive:
    """
    Cognitive extension of BOFCore.
    Adds EventBus, PolicyGate, and RouterHybrid for adaptive orchestration.
    """

    def __init__(self, acf=None, ais=None, bpb=None, skill_executor=None, intent_detector=None, event_log_path="data/log/events.jsonl"):
        self.acf = acf
        self.ais = ais
        self.bpb = bpb
        self.event_bus = EventBus(event_log_path)
        self.policy_gate = PolicyGate()
        self.router = RouterHybrid()
        # Optional callable: (skill_name:str, input_text:str)->Any
        self.skill_executor = skill_executor
        self.intent_detector = intent_detector

    def initialize(self):
        print("[BOF-ADAPTIVE] Initializing cognitive orchestrator...")
        if self.acf:
            print(" - ACF module attached.")
        if self.ais:
            print(" - AIS module attached.")
        if self.bpb:
            print(" - BPB module attached.")
        print("[BOF-ADAPTIVE] System ready for adaptive orchestration.")

    def sense(self, input_text):
        print("[BOF-ADAPTIVE] Sense phase: capturing input...")
        self.event_bus.publish("InputEvent", {"text": input_text})
        if self.ais:
            ais_state = self.ais.emit_state("Focus")
            self.event_bus.publish("AISState", {"state": ais_state})
        return input_text

    def interpret(self, input_text):
        print("[BOF-ADAPTIVE] Interpret phase: behavioral adaptation...")
        if self.acf:
            adapted_text = self.acf.adapt_style(input_text, mode="Standard")
            self.event_bus.publish("ACFAdapt", {"mode": "Standard"})
            return adapted_text
        return input_text

    def plan(self, intent="writing", modes=None):
        print("[BOF-ADAPTIVE] Plan phase: selecting route...")
        ais_state = "Focus"
        acf_mode = "Standard"
        selected_skill = self.router.decide(intent, ais_state, acf_mode, modes=modes)
        self.event_bus.publish("RouteDecision", {"skill": selected_skill, "modes": modes})
        return selected_skill

    def consent(self, action="execute"):
        print("[BOF-ADAPTIVE] Consent phase: verifying policies...")
        if self.policy_gate.check(action):
            self.event_bus.publish("Consent", {"approved": True})
            return True
        return False

    def execute(self, skill_name, input_text):
        print("[BOF-ADAPTIVE] Execute phase: running BPB skill cycle...")
        result = None
        if self.bpb:
            try:
                result = self.bpb.run_skill(
                    skill_name,
                    input_text,
                    skill_executor=self.skill_executor,
                )
            except Exception as e:
                print(f"[BOF-ADAPTIVE] Error executing skill: {e}")
        else:
            print("[BOF-ADAPTIVE] No BPB module attached.")
        payload = {
            "skill": skill_name,
            "input": input_text,
        }
        if isinstance(result, dict):
            payload["output"] = {
                "text": result.get("text"),
                "scores": result.get("scores"),
            }
        elif isinstance(result, str):
            payload["output"] = {"text": result}
        self.event_bus.publish("Execution", payload)
        return result

    def reflect(self):
        print("[BOF-ADAPTIVE] Reflect phase: logging and continuity...")
        last_event = self.event_bus.fetch_latest()
        print(f"[BOF-ADAPTIVE] Last event recorded: {last_event}")
        if self.event_bus.persist_path:
            print(f"[BOF-ADAPTIVE] Events persisted to {self.event_bus.persist_path}")

    def run(self, intent="writing", input_text=None):
        print(f"[BOF-ADAPTIVE] Starting adaptive orchestration for intent={intent}")
        sensed = self.sense(input_text)
        interpreted = self.interpret(sensed)
        detected_modes = None
        if self.intent_detector:
            try:
                self.intent_detector.collect_sample(sensed)
                self.intent_detector.cluster_modes()
                detected_modes = self.intent_detector.get_modes()
            except Exception as e:
                print(f"[BOF-ADAPTIVE] Intent detector error: {e}")

        plan = self.plan(intent, modes=detected_modes)
        if self.consent(action=plan):
            self.execute(plan, interpreted)
        self.reflect()
        print("[BOF-ADAPTIVE] Cycle complete.")

