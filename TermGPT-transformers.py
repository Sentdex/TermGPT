import colorama
import subprocess
import re
import requests
from bs4 import BeautifulSoup

# Load and set up the key
DEBUG = True
message_history = []
TERMINAL_COMMANDS = []
READ_RE_PATTERN = r"--r \[(.*?)\]"
WEB_RE_PATTERN = r"--w \[(.*?)\]"


from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline

MODEL_PATH = "models/wizardLM-7B-HF"

def initialize_colorama():
    for _ in range(3):
        print()
    print(f"~{colorama.Style.BRIGHT}\033[4mWelcome to TermGPT{colorama.Style.RESET_ALL}~")
    for _ in range(3):
        print()

def clear_context():
    global message_history
    global TERMINAL_COMMANDS
    message_history = TERMINAL_COMMANDS
    print(colorama.Fore.YELLOW + colorama.Style.BRIGHT + "Context reset.\n\n" + colorama.Style.RESET_ALL)

def extract_paragraphs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = ''
    for para in soup.find_all('p'):
        paragraphs += para.text + '\n\n'
    return paragraphs

def process_file_matches(matches):
    match_content = {}
    for n, match in enumerate(matches):
        with open(match, "r") as f:
            match_content[match] = f.read()
    return match_content

def process_web_matches(web_matches):
    web_match_content = {}
    for n, web_match in enumerate(web_matches):
        web_match_content[web_match] = extract_paragraphs(web_match)
    return web_match_content

def preprocess_input(init_input):
    matches = re.findall(READ_RE_PATTERN, init_input)
    web_matches = re.findall(WEB_RE_PATTERN, init_input)
    match_content = process_file_matches(matches)
    web_match_content = process_web_matches(web_matches)

    for match in match_content:
        original = f"--r [{match}]"
        replacement = f"\n file: {match}\n{match_content[match]}\n"
        init_input = init_input.replace(original, replacement)

    for web_match in web_match_content:
        original = f"--w [{web_match}]"
        replacement = f"\n website content: {web_match}\n{web_match_content[web_match]}\n"
        init_input = init_input.replace(original, replacement)

    user_input = "NEW STARTING INPUT: " + init_input
    return user_input


def run_command(command):
    print(f"{colorama.Fore.YELLOW}Running command: {command}{colorama.Style.RESET_ALL}")
    command_output = subprocess.check_output(command, shell=True, universal_newlines=True)
    print(command_output)
    return command_output

def main():
    # app
    initialize_colorama()
    command_outputs = ""
    WIZARD_DONE = False

    # init llm (wizzard7b)
    print(colorama.Fore.YELLOW + colorama.Style.BRIGHT + "Loading wizard model..." + colorama.Style.RESET_ALL)    
    wizard_model = GPT2LMHeadModel.from_pretrained(MODEL_PATH)
    wizard_tokenizer = GPT2Tokenizer.from_pretrained(MODEL_PATH)
    wizard = pipeline('text-generation', model=wizard_model, tokenizer=wizard_tokenizer)
    print(colorama.Fore.GREEN + colorama.Style.BRIGHT + "Wizard model loaded." + colorama.Style.RESET_ALL)
    
    while True:
        print(colorama.Fore.CYAN + "Enter your command or type '--c' to clear the context:")
        print(colorama.Fore.CYAN + "You can also use '--r [path/to/file.py]' to open and read a file into context, or '--w [url]' to parse a website into context.")
        init_input = input(colorama.Fore.GREEN + colorama.Style.BRIGHT + "Command: " + colorama.Style.RESET_ALL)

        if init_input.lower() == "clear" or init_input.lower() == "--c":
            clear_context()
            command_outputs = ""
            continue

        user_input = preprocess_input(init_input)

        if DEBUG:
            print()
            print()
            print("User Input:")
            print()
            print(colorama.Fore.MAGENTA + colorama.Style.DIM + user_input + colorama.Style.RESET_ALL)
            print()
            print()

        message_history.append({"role": "user", "content": user_input})
        commands = []

        while not WIZARD_DONE:
            prompt = "\n".join([msg['content'] for msg in message_history])
            generated = wizard(prompt, max_length=1024, do_sample=True, temperature=0.7, top_p=0.9, repetition_penalty=1.2, num_return_sequences=1)
            wizard_response = generated[0]['generated_text'].split("\n")[-1]
            print(f"{colorama.Fore.MAGENTA}Wizard Output:{colorama.Style.RESET_ALL}\n{wizard_response}\n")

            if "anything else?" in wizard_response:
                WIZARD_DONE = True

            message_history.append({"role": "wizard", "content": wizard_response})
            wizard_commands = re.findall(r"\$(.*?)\$", wizard_response)
            if wizard_commands:
                for command in wizard_commands:
                    commands.append(command)

        for command in commands:
            command_output = run_command(command)
            command_outputs += command_output

if __name__ == "__main__":
    main()
