# Shared prompt payloads for BOF demos

WRITING_REWRITE_INSTRUCTION = "Read and rewrite the text preserving: [variables]."
WRITING_REWRITE_TEXT = (
    "People exceed the expectations when they do have both: incentives, "
    "and their ideas are part of the solution."
)


def compose_writing_instruction_payload() -> str:
    """Return the exact instruction+text payload shared across demos."""
    return f"{WRITING_REWRITE_INSTRUCTION}\n\n{WRITING_REWRITE_TEXT}"

