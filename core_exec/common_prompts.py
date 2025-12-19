# Shared prompt payloads for BOF demos

WRITING_REWRITE_INSTRUCTION = (
    "Expand the following sentence into a short paragraph. Add more details about the setting, "
    "the animals, and their actions, while maintaining the simplicity and clarity of the original sentence."
)
WRITING_REWRITE_TEXT = "The cat jumped over the fence, and the dog barked loudly."

READING_SUMMARY_PROMPT = (
    "Read the following text and provide a detailed analysis of the key events. Identify the central actions, "
    "motivations, and underlying themes. Summarize the text in a way that highlights not only the plot but also "
    "the emotional tone and relationships between the characters. Your summary should focus on the progression "
    "of the narrative and the dynamics between the people and the environment."
)
READING_SUMMARY_TEXT = (
    "The train arrived at the station just as the sun began to rise. Passengers hurriedly disembarked, eager "
    "to start their day. A couple sat on a bench, holding hands, while others made their way to the exit. "
    "The station was bustling, yet there was a sense of calmness in the air as people began their routines."
)


def compose_writing_instruction_payload() -> str:
    """Return the exact instruction+text payload shared across demos."""
    return f"{WRITING_REWRITE_INSTRUCTION}\n\n{WRITING_REWRITE_TEXT}"


def compose_reading_instruction_payload() -> str:
    """Return only the reading text; the system prompt lives in ReadingSkill."""
    return READING_SUMMARY_TEXT
