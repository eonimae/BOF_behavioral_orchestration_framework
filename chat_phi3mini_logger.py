# chat_phi3mini_logger.py
import datetime
import subprocess

try:
    import ollama
except Exception as e:
    ollama = None

MODEL = "phi3:mini"
context = []
logfile = f"logs/chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

import os
os.makedirs('logs', exist_ok=True)

print("Local chat with phi3-mini (type 'exit' to quit)")
print("Commands: /alone (writing baseline) | /alone_reading (reading baseline) | /bof (full framework)\n")
print(f"Saving traces to: {logfile}\n")

while True:
    user_input = input("YOU: ").strip()

    if user_input.lower() in ["exit", "salir", "quit"]:
        break

    # === COMANDOS ===
    if user_input.startswith("/"):
        command = user_input[1:].lower()

        if command == "alone":
            print("\n>>> Running baseline (phi3-mini alone)...\n")
            subprocess.run(["python", "-m", "core_exec.skills.writing_phi3mini_alone"])
            print("\n>>> Baseline finished.\n")
            continue

        elif command == "alone_reading":
            print("\n>>> Running reading baseline (phi3-mini alone)...\n")
            subprocess.run(["python", "-m", "core_exec.skills.reading_phi3mini_alone"])
            print("\n>>> Reading baseline finished.\n")
            continue

        elif command == "bof":
            print("\n>>> Running full BOF...\n")
            subprocess.run(["python", "main.py"])
            print("\n>>> BOF execution finished.\n")
            continue

        else:
            print(f"Unrecognized command: {command}")
            continue

    # === CHAT NORMAL ===
    if ollama is None:
        msg = "[warn] Ollama unavailable. Please install and try again."
        print(msg)
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(f"YOU: {user_input}\nphi3-mini: {msg}\n\n")
        continue

    context.append({'role': 'user', 'content': user_input})
    try:
        response = ollama.chat(model=MODEL, messages=context)
        message = response['message']['content']
    except Exception as e:
        message = f"[error] Error calling Ollama: {e}"

    print(f"phi3-mini: {message}\n")
    context.append({'role': 'assistant', 'content': message})

    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"YOU: {user_input}\nphi3-mini: {message}\n\n")
