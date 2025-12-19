# writing_phi3mini_alone.py
# Baseline test: phi-3-mini standalone (no BOF orchestration)

from typing import Optional

try:
    import ollama
except Exception:
    ollama = None

from core_exec.skills.writing import (
    WritingSkill,
    REWRITE_SYSTEM_PROMPT,
    _fallback_rewrite,
    _truncate_words,
)
from core_exec.common_prompts import (
    WRITING_REWRITE_INSTRUCTION,
    WRITING_REWRITE_TEXT,
)


def run_baseline() -> None:
    text = _truncate_words(WRITING_REWRITE_TEXT, 100)
    instruction_payload = f"{WRITING_REWRITE_INSTRUCTION}\n\n{text}"

    if ollama is None:
        print("[warn] Ollama unavailable. Please install and try again.")
        rewritten = _fallback_rewrite(text)
        _print_result(text, rewritten, None)
        return

    skill = WritingSkill()
    provider = skill.provider

    try:
        if provider is None:
            raise RuntimeError("Ollama provider unavailable")
        response = provider.chat(
            model=skill.model,
            messages=[
                {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
                {"role": "user", "content": instruction_payload},
            ],
            options={"temperature": 0.7, "top_p": 1.0},
        )
        rewritten = response["message"]["content"]
        if len(rewritten.split()) > 100:
            rewritten = _truncate_words(rewritten, 100)
            print("[baseline] Warning: model exceeded 100 words, truncated safely.")
        else:
            print("[baseline] Model output within 100-word constraint.")
    except Exception as exc:
        print(f"[warn] Model rephrase failed ({exc}); using fallback.")
        rewritten = _fallback_rewrite(text)

    scores: Optional[dict] = None
    try:
        scores = skill._evaluate_with_model(rewritten)  # type: ignore[attr-defined]
    except Exception as exc:
        print(f"[warn] Evaluation failed ({exc}); skipping scores.")

    _print_result(text, rewritten, scores)


def _print_result(original: str, rewritten: str, scores: Optional[dict]) -> None:
    print("\n=== BASELINE phi3:mini (no BOF) ===")
    print("Original text (<=100 words):")
    print(original)
    print("\nRephrased output:")
    print(rewritten)
    if scores:
        print("\nScores")
        print(
            f"Clarity: {scores.get('clarity', 0):.2f} | "
            f"Coherence: {scores.get('coherence', 0):.2f} | "
            f"Tone: {scores.get('tone', 0):.2f}"
        )
    print("====================================\n")


if __name__ == "__main__":
    run_baseline()
