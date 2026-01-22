# writing.py
# Behavioral Skill: Writing (Functional + phi3:mini Integration, JSON-safe + Adaptive Refinement)

import re
import textwrap
import json
from typing import Dict, List, Optional, Tuple

try:
    from BOF_CORE.core_exec.providers.model_provider import OllamaProvider, BaseModelProvider  # when installed as package
except Exception:
    try:
        from core_exec.providers.model_provider import OllamaProvider, BaseModelProvider
    except Exception:
        OllamaProvider = None  # type: ignore
        BaseModelProvider = object  # type: ignore


class WritingSkill:
    """
    Core skill module for Writing.
    Each layer (L1–L5) performs a distinct behavioral operation on text.
    L2 and L3 use phi3:mini for real generative output.
    L4 generates and applies adaptive refinements.
    """

    def __init__(self, provider: Optional[BaseModelProvider] = None, model: str = 'phi3:mini'):
        self.history = []
        self.score = {"clarity": 0, "coherence": 0, "tone": 0}
        self.model = model
        # Default to Ollama provider if available
        if provider is not None:
            self.provider = provider
        else:
            self.provider = _get_default_provider()
        print("[WritingSkill] Initialized (Functional + phi3:mini JSON-safe + Adaptive Refinement).")

    # === L1: Validation Layer ===
    def L1_validate(self, text):
        print("[L1] Validation layer - checking input integrity...")
        if not text or not text.strip():
            return "[Error] Empty text."
        if len(text) < 10:
            return "[Error] Text too short."
        if not re.search(r"[a-zA-Z]", text):
            return "[Error] Non-linguistic input."
        cleaned = re.sub(r"\s+", " ", text.strip())
        cleaned = _truncate_words(cleaned, 100)
        self.history.append(("L1", {"status": "validated", "words": len(cleaned.split())}))
        print("[L1] Input validated successfully.")
        return cleaned

    # === L2: Iteration Layer (uses phi3:mini for rephrasing) ===
    def L2_iterate(self, text):
        print("[L2] Iteration layer - generating rephrased text via phi3:mini...")
        try:
            response = None
            if self.provider is not None:
                limited_prompt = (
                    "Rephrase the following text so it preserves its full meaning "
                    "and coherence but stays within 100 words total. "
                    "Do not truncate mid-idea; compress elegantly if needed.\n\n"
                    f"Text:\n{text}"
                )
                response = self.provider.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
                        {"role": "user", "content": limited_prompt},
                    ],
                    options={"temperature": 0.7, "top_p": 1.0},
                )
            new_text = response["message"]["content"]
            if len(new_text.split()) > 100:
                new_text = _truncate_words(new_text, 100)
                print("[L2] Warning: model exceeded 100 words, truncated safely.")
            else:
                print("[L2] Model output within 100-word constraint.")
            print("\n[L2 OUTPUT] ------------------------------------------")
            print(new_text)
            print("------------------------------------------------------\n")
            self.history.append(("L2", "iterated"))
            return new_text
        except Exception as e:
            print(f"[L2] Fallback due to error: {e}")
            return _fallback_rewrite(text)

    # === L3: Evaluation Layer (JSON-safe parsing) ===
    def L3_evaluate(self, text):
        print("[L3] Evaluation layer - assessing clarity, coherence, and tone via phi3:mini...")
        try:
            parsed_scores = self._evaluate_with_model(text)
            if not parsed_scores:
                raise ValueError("Model evaluation returned empty scores.")
            self.score = parsed_scores
            self.history.append(("L3", dict(self.score)))
            return (
                f"Scores -> clarity:{self.score['clarity']:.2f}, "
                f"coherence:{self.score['coherence']:.2f}, "
                f"tone:{self.score['tone']:.2f}"
            )
        except Exception as e:
            print(f"[L3] Evaluation fallback due to error: {e}")
            self.score.update(_heuristic_scores(text))
            return f"Scores -> clarity:{self.score['clarity']:.2f}, coherence:{self.score['coherence']:.2f}, tone:{self.score['tone']:.2f}"

    def _evaluate_with_model(self, text: str) -> Optional[Dict[str, float]]:
        if self.provider is None:
            return None
        prompt = EVAL_PROMPT_TEMPLATE.format(text=text)
        attempts = 0
        while attempts < 2:
            response = self.provider.chat(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                options={"temperature": 0, "top_p": 1.0, "seed": 0},
            )
            raw = response["message"]["content"]
            parsed = _parse_scores(raw)
            if parsed:
                return parsed
            attempts += 1
        return None

    # === L4: Feedback + Refinement Layer ===
    def L4_feedback_and_refine(self, text):
        print("[L4] Feedback layer - generating suggestions and refinements...")

        suggestions = self._generate_suggestions()
        print(f"[L4] Suggestions:\n{suggestions}")

        refined_text = self._apply_refinements(text, suggestions)
        print(f"\n[L4] Refined text:\n{refined_text}\n")

        self.history.append(("L4", {"suggestions": suggestions, "refined": refined_text}))
        return refined_text

    def _generate_suggestions(self):
        suggestions = []
        if self.score["clarity"] < 0.75:
            suggestions.append("- Clarity could be improved: consider shorter sentences.")
        if self.score["coherence"] < 0.75:
            suggestions.append("- Coherence needs work: add transitional phrases.")
        if self.score["tone"] < 0.75:
            suggestions.append("- Tone adjustment needed: balance formality.")
        return "\n".join(suggestions) if suggestions else "- Text is well-structured."

    def _apply_refinements(self, text, suggestions):
        try:
            refine_prompt = f"""
            Original text: {text}

            Improvement suggestions:
            {suggestions}

            Rewrite the text applying these suggestions. Keep the core meaning but improve based on feedback.
            """
            response = None
            if self.provider is not None:
                response = self.provider.chat(
                    model=self.model,
                    messages=[
                    {'role': 'system', 'content': 'You are a text refinement assistant. Apply suggestions precisely.'},
                    {'role': 'user', 'content': refine_prompt}
                    ]
                )
            return response['message']['content']
        except Exception as e:
            print(f"[L4] Refinement error: {e}")
            return _fallback_rewrite(text)

    # === L5: Calibration Layer ===
    def L5_calibrate(self):
        print("[L5] Calibration layer - updating internal metrics...")
        avg = sum(self.score.values()) / 3
        self.history.append(("L5", {"average_score": round(avg, 2)}))
        print(f"[L5] Calibration complete. Avg={avg:.2f}")
        return avg

    # === Full Skill Cycle (Evolutive Mode) ===
    def run(self, text):
        print("[WritingSkill] Starting skill execution (adaptive refinement mode)...")
        versions = {}

        text = self.L1_validate(text)
        if text.startswith("[Error]"):
            print(f"[WritingSkill] Aborted -> {text}")
            return text
        versions["L1_cleaned"] = text

        text = self.L2_iterate(text)
        versions["L2_rephrased"] = text

        eval_report = self.L3_evaluate(text)
        versions["L3_evaluation"] = eval_report

        refined_text = self.L4_feedback_and_refine(text)
        versions["L4_refined_text"] = refined_text

        avg = self.L5_calibrate()
        versions["L5_final_avg"] = avg

        print("\n=== TEXT EVOLUTION TRACE ===")
        print(f"[L1] Cleaned input:\n{versions['L1_cleaned']}\n")
        print(f"[L2] Rephrased version:\n{versions['L2_rephrased']}\n")
        print(f"[L3] Evaluation report:\n{versions['L3_evaluation']}\n")
        print(f"[L4] Refined version after feedback:\n{versions['L4_refined_text']}\n")
        print(f"[L5] Final average score: {versions['L5_final_avg']:.2f}")
        print("=== END OF TRACE ===\n")

        print("[WritingSkill] Skill execution complete.")
        return {
            "text": versions["L4_refined_text"],
            "scores": dict(self.score),
            "history": list(self.history),
            "versions": versions,
        }


# Simple callable hook for future tool/skill exposure
def skill_writing(text: str) -> str:
    skill = WritingSkill()
    output = skill.run(text)
    if isinstance(output, dict):
        return output.get("text", "")
    return output


def _get_default_provider() -> Optional[BaseModelProvider]:
    if OllamaProvider is None:
        return None
    global _CACHED_PROVIDER
    try:
        return _CACHED_PROVIDER
    except NameError:
        pass
    try:
        _CACHED_PROVIDER = OllamaProvider()
    except Exception:
        _CACHED_PROVIDER = None
    return _CACHED_PROVIDER


def _fallback_rewrite(text: str) -> str:
    sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", text)
        if s and s.strip()
    ]
    if not sentences:
        return text
    connectors = [
        "Additionally",
        "Furthermore",
        "Consequently",
        "Therefore",
    ]
    rewritten: List[str] = [sentences[0]]
    for idx, sentence in enumerate(sentences[1:], start=1):
        connector = connectors[(idx - 1) % len(connectors)]
        lowered = sentence[0].lower() + sentence[1:] if len(sentence) > 1 else sentence.lower()
        rewritten.append(f"{connector}, {lowered}")
    combined = " ".join(rewritten)
    return textwrap.shorten(combined, width=400, placeholder="...")


def _clamp(value: float, bounds: Tuple[float, float] = (0.0, 1.0)) -> float:
    low, high = bounds
    return max(low, min(high, round(value, 2)))


def _truncate_words(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    truncated = " ".join(words[:limit])
    return truncated


EVAL_PROMPT_TEMPLATE = """Evaluate this text using 3 independent criteria. Respond ONLY in this format:
CLARITY: 0.XX
COHERENCE: 0.XX
TONE: 0.XX

Use exactly two decimal places for each score.
Assess each criterion independently; do not average or compensate.

Rubric:
Clarity (0-1): Is each sentence understandable without re-reading?
  1.00 = direct and clear
  0.75 = mostly clear, minor density
  0.50 = confusing, requires re-reading
  0.25 = very confusing, unexplained terms/acronyms
  0.00 = unreadable

Coherence (0-1): Do ideas progress logically?
  1.00 = fluent, cohesive, no contradictions
  0.75 = minor jumps but the thread holds
  0.50 = disorganized, abrupt topic shifts
  0.25 = chaotic, missing transitions
  0.00 = unrelated ideas

Tone (0-1): Is the register consistent with the intent?
  1.00 = tone remains stable throughout
  0.75 = small acceptable variations
  0.50 = noticeable shifts without justification
  0.25 = mixed registers with little control
  0.00 = chaotic tone, incompatible with purpose

Text to evaluate:
{text}

Scores:
"""


def _heuristic_scores(text: str) -> Dict[str, float]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s for s in sentences if s]
    avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    long_sentences = sum(1 for s in sentences if len(s.split()) > 35)
    unclear = long_sentences or avg_len > 30

    clarity = 1.0
    if unclear:
        clarity = 0.5 if long_sentences else 0.75
    if not sentences:
        clarity = 0.0

    transitions = len(re.findall(r"\b(however|therefore|then|because|but)\b", text, re.IGNORECASE))
    coherence = 1.0
    if len(sentences) <= 1:
        coherence = 0.5
    elif transitions == 0 and len(sentences) > 2:
        coherence = 0.75

    tone = 1.0
    if text.count("!") >= 2 or re.search(r"\b(lol|haha)\b", text.lower()):
        tone = 0.5
    if any(word in text.lower() for word in ["urgent", "crisis"]) and "!" in text:
        tone = 0.25

    return {
        "clarity": _nearest_band(clarity),
        "coherence": _nearest_band(coherence),
        "tone": _nearest_band(tone),
    }


def _nearest_band(value: float) -> float:
    bands = [0.0, 0.25, 0.5, 0.75, 1.0]
    closest = min(bands, key=lambda b: abs(b - value))
    return closest


def _parse_scores(response: str) -> Optional[Dict[str, float]]:
    pattern = re.compile(r"^(clarity|coherence|tone)\s*:\s*([01]\.\d{2})$", re.IGNORECASE | re.MULTILINE)
    matches = pattern.findall(response)
    if len(matches) < 3:
        return None
    scores: Dict[str, float] = {}
    for key, value in matches:
        try:
            scores[key.lower()] = float(value)
        except ValueError:
            return None
    if {"clarity", "coherence", "tone"} <= scores.keys():
        return scores
    return None


def _evaluate_with_model(self, text: str) -> Optional[Dict[str, float]]:
    if self.provider is None:
        return None
    prompt = EVAL_PROMPT_TEMPLATE.format(text=text)
    attempts = 0
    while attempts < 2:
        response = self.provider.chat(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            options={"temperature": 0, "top_p": 1.0, "seed": 0},
        )
        raw = response["message"]["content"]
        parsed = _parse_scores(raw)
        if parsed:
            return parsed
        attempts += 1
    return None
REWRITE_SYSTEM_PROMPT = "Rephrase and slightly expand the following text while keeping its meaning and tone natural."
