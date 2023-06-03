import colorama
import subprocess
import re
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError

# Load and set up the key
DEBUG = True
message_history = []
TERMINAL_COMMANDS = []
READ_RE_PATTERN = r"--r \[(.*?)\]"
WEB_RE_PATTERN = r"--w \[(.*?)\]"

# API settings
API_HOST = 'localhost:5000'
API_URI = f'http://{API_HOST}/api/v1/generate'

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

def generate_prompt(prompt):
    request = {
        'prompt': prompt,
        'max_new_tokens': 250,
        'do_sample': True,
        'temperature': 1.3,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    try:
        response = requests.post(API_URI, json=request)

        if response.status_code == 200:
            result = response.json()['results'][0]['text']
            return result
        else:
            return None
    except ConnectionError as e:
        error_message = str(e)
        error_message = f"Connection Error: {error_message}"
        return error_message

def main():
    # app
    initialize_colorama()
    command_outputs = ""
    WIZARD_DONE = False
    
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
            wizard_response = generate_prompt(prompt)
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
