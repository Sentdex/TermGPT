import re
import os
import time
import openai
import requests
import colorama
import logging
import subprocess
from contexts import TERMINAL_COMMANDS
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

DEBUG = False
logging.basicConfig(level=logging.WARNING)
message_history = TERMINAL_COMMANDS
READ_RE_PATTERN = r"--r \[(.*?)\]"
WEB_RE_PATTERN = r"--w \[(.*?)\]"


def gpt_query(model="gpt-4", max_retries=15, sleep_time=2):
    global message_history
    retries = 0
    logger = logging.getLogger()

    logger.info("Message History: %s", message_history)

    while retries < max_retries:
        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=message_history
            )
            reply_content = completion.choices[0].message.content
            if reply_content:
                return reply_content
        except Exception as e:
            logger.warning("Error during gpt_query(): %s", e)
            retries += 1
            time.sleep(sleep_time)

    raise Exception("Maximum retries exceeded. Check your code for errors.")


def extract_paragraphs(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs: str = ''

    for paragraph in soup.find_all('p'):
        paragraphs += paragraph.text + '\n\n'
    return paragraphs


# Added functions

######## Change a command
def change_cmd(commands, ind):
    new_cmd = input("What's the new command that you want to have as command number " + str(ind) + " ? ")
    if len(new_cmd) == 0:
        print("You can't replace a command with null text. If you want to delete the command " + str(
            ind) + ", try option 2 in the menu")
    else:
        commands[ind] = new_cmd
        print("Here is the new list of commands: ")
        print_commands(commands)


def change_command():
    ind = int(input("What command do you want to change ? "))
    chg_command = input("Change command " + str(ind) + "? (y/n): ")
    if chg_command.lower() == "y":
        change_cmd(commands, ind)
    else:
        print(colorama.Fore.CYAN + colorama.Style.BRIGHT + "Okay, not changing command " + str(
            ind) + "." + colorama.Style.RESET_ALL)


###### Delete a command
def del_cmd(commands, ind):
    del_comm = commands.pop(ind)
    print("\"" + del_comm + '\" has been deleted successfully!')
    print("Here is the new list of commands: ")
    print_commands(commands)


def delete_command():
    ind = int(input("What command do you want to delete ? "))
    if ind not in range(len(commands) + 1):
        print("This command doesn't exist")
        return
    del_command = input("Delete command " + str(ind) + "? (y/n): ")
    if del_command.lower() == "y":
        del_cmd(commands, ind)
    else:
        print(colorama.Fore.CYAN + colorama.Style.BRIGHT + "Okay, not deleting command " + str(
            ind) + "." + colorama.Style.RESET_ALL)


####### Add a command
def add_cmd(commands, cmd, ind):
    commands.insert(ind, cmd)
    print("Command has been successfully added! Here is the new list of commands: ")
    print_commands(commands)


def add_command():
    ind = int(input("At what position do you want your new command to be at? "))
    if ind < 0:
        print("Invalid position")
        return
    cmd = input("Input the command to add at position " + str(ind) + " : ")
    if len(cmd) == 0:
        print("You can't add an empty command")
        return
    add_cmmd = input("Add command: \"" + cmd + "\" at position " + str(ind) + "? (y/n): ")
    if add_cmmd.lower() == "y":
        add_cmd(commands, cmd, ind)
    else:
        print(colorama.Fore.CYAN + colorama.Style.BRIGHT + "Okay, not adding command \"" + str(
            cmd) + "\"." + colorama.Style.RESET_ALL)


###### Explain a command
def explain_cmd(model, message_history, commands, ind):
    comm = commands[ind]
    explain_prompt = "I want you to explain this command that you gave me: \"" + comm + "\""
    message_history.append({"role": "user", "content": explain_prompt})
    try:
        explain_completion = openai.ChatCompletion.create(
            model=model,
            messages=message_history
        )
        explanation = explain_completion.choices[0].message.content
        if explanation:
            print(explanation)
            return explanation
    except Exception as e:
        print(
            colorama.Fore.YELLOW + colorama.Style.DIM + "Error during gpt_query() " + str(e) + colorama.Style.RESET_ALL)
        time.sleep(25)


def explain_command():
    ind = int(input("What command do you want TermGPT to explain ? "))
    if ind < 0:
        print("Invalid position")
        return
    explain_cmd(message_history, commands, ind, model="gpt-4")


###### Export as text file
def export_txt(filename, commands):
    with open(filename, 'w') as output:
        for cmd in commands:
            output.write(str(cmd) + '\n')
    print("Commands exported successfully to " + filename)


def export_commands_txt():
    filename = input("What do you want to call the txt file? ")
    if len(filename) == 0: return
    if '.txt' not in filename: filename = filename + '.txt'
    exp_commands = input("Export commands to " + filename + " (y/n): ")
    if exp_commands.lower() == "y":
        export_txt(filename, commands)
    else:
        print(
            colorama.Fore.CYAN + colorama.Style.BRIGHT + "Okay, not exporting to " + filename + ".txt" + colorama.Style.RESET_ALL)


###### Export as shell script
def export_sh(shname, commands):
    with open(shname, "w") as file:
        # Write the shebang line (optional)
        file.write("#!/bin/bash\n")

        # Write each command to the file
        for command in commands:
            file.write(command + "\n")


def export_commands_sh():
    shname = input("What do you want to call the sh script? ")
    if len(shname) == 0: return
    if '.sh' not in shname: shname = shname + '.sh'
    sh_commands = input("Export commands to " + shname + " (y/n): ")
    if sh_commands.lower() == "y":
        export_sh(shname, commands)
    else:
        print(
            colorama.Fore.CYAN + colorama.Style.BRIGHT + "Okay, not exporting to " + shname + "" + colorama.Style.RESET_ALL)


command_outputs = ""


###### Run commands
def run_cmds(commands):
    global command_outputs
    for n, command in enumerate(commands):
        try:
            print(colorama.Fore.CYAN + colorama.Style.BRIGHT + "Running command " + str(
                n) + ": " + command + colorama.Style.RESET_ALL)
            output = subprocess.check_output(command, shell=True, text=True).strip()

        except subprocess.CalledProcessError as e:
            print(colorama.Fore.YELLOW + colorama.Style.DIM + "Error during command execution: " + str(
                e) + colorama.Style.RESET_ALL)
            output = e.output.strip()
        print(output)
        command_outputs += output + "\n\n"


def run_commands():
    print(
        colorama.Fore.CYAN + colorama.Style.BRIGHT + "Would you like to run these commands? " + colorama.Fore.YELLOW + "Read carefully!" + colorama.Style.RESET_ALL + colorama.Fore.CYAN + colorama.Style.BRIGHT + " Do not run if you don't understand and want the outcomes. (y/n)" + colorama.Style.RESET_ALL)
    run_cmd = input("Run the commands? (y/n): ")
    if run_cmd.lower() == "y":
        run_cmds(commands)
    else:
        print(colorama.Fore.CYAN + colorama.Style.BRIGHT + "Okay, not running commands." + colorama.Style.RESET_ALL)


def print_commands(commands):
    for n, cmd in enumerate(commands):
        print(str(n) + "-  " + cmd)


options = {
    1: change_command,
    2: delete_command,
    3: add_command,
    # 4: explain_command,
    4: export_commands_txt,
    5: export_commands_sh,
    6: run_commands
}


def print_menu():
    print('What do you want to do with these commands ?')
    print('1 - Change a command')
    print('2 - Delete a command')
    print('3 - Add a command')
    # print('4 - Ask TermGPT to explain a command')
    print('4 - Export commands as a text file')
    print('5 - Export commands as a shell script')
    print('6 - Run commands')
    print('7 - Start a new prompt')
    print('8 - Quit')


# Welcome message
for _ in range(3): print()
print(f"~{colorama.Style.BRIGHT}\033[4mWelcome to TermGPT{colorama.Style.RESET_ALL}~")
for _ in range(3): print()

print("The goal for TermGPT is to make rapid prototyping with GPT models even quicker and more fluid.")
print()

command_outputs = ""

while True:
    GPT_DONE = False
    print(
        colorama.Fore.CYAN + colorama.Style.BRIGHT + 'It looks like there is no current input. Please provide your objectives. \n"'
        + colorama.Fore.YELLOW + '--c' + colorama.Fore.CYAN + '" to clear contextual history. \n"'
        + colorama.Fore.YELLOW + '--o' + colorama.Fore.CYAN + '" to parse previous console command outputs and suggest further commands (can be helpful for big errors)\n"'
        + colorama.Fore.YELLOW + '--w' + colorama.Fore.CYAN + '" to parse a website into context \n"'
        + colorama.Fore.YELLOW + '--r [path/to/file.py]' + colorama.Fore.CYAN + '" to open and read some file into context (can do multiple files, and is embedded into some prompt.) Example: "Please change --r [mplexample.py] to be a dark theme"' + colorama.Style.RESET_ALL)

    init_input = input(colorama.Fore.GREEN + colorama.Style.BRIGHT + "Command: " + colorama.Style.RESET_ALL)

    if init_input.lower() == "clear" or init_input.lower() == "--c":
        message_history = TERMINAL_COMMANDS
        command_outputs = ""
        print(colorama.Fore.YELLOW + colorama.Style.BRIGHT + "Context reset.\n\n" + colorama.Style.RESET_ALL)
        continue

    elif init_input.lower() == "output" or init_input.lower() == "--o":
        user_input = "NEW STARTING INPUT: I received the following console outputs after running everything. Is there anything I should do to address any errors, warnings, or notifications?: \n" + command_outputs

    else:
        matches = re.findall(READ_RE_PATTERN, init_input)
        match_content = {}
        if matches:
            for n, match in enumerate(matches):
                with open(match, "r") as f:
                    match_content[match] = f.read()

        web_matches = re.findall(WEB_RE_PATTERN, init_input)
        web_match_content = {}
        if web_matches:
            for n, web_match in enumerate(web_matches):
                web_match_content[web_match] = extract_paragraphs(web_match)

        for match in match_content:
            original = f"--r [{match}]"
            replacement = f"\n file: {match}\n{match_content[match]}\n"
            init_input = init_input.replace(original, replacement)

        for web_match in web_match_content:
            original = f"--w [{web_match}]"
            replacement = f"\n website content: {web_match}\n{web_match_content[web_match]}\n"
            init_input = init_input.replace(original, replacement)

        user_input = "NEW STARTING INPUT: " + init_input

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

    while not GPT_DONE:
        print(
            colorama.Fore.GREEN + colorama.Style.DIM + "Querying GPT for next command (these are not running yet)..." + colorama.Style.RESET_ALL)
        reply_content = gpt_query(model="gpt-4")

        message_history.append({"role": "assistant", "content": reply_content})
        message_history.append({"role": "user", "content": "NEXT"})
        print(colorama.Fore.WHITE + colorama.Style.DIM + reply_content + colorama.Style.RESET_ALL)

        if reply_content.lower().startswith("done"):
            GPT_DONE = True
            print(colorama.Fore.YELLOW + colorama.Style.BRIGHT + "Done reached." + colorama.Style.RESET_ALL)
            break
        else:
            commands.append(reply_content)
        time.sleep(1.5)

    print(colorama.Fore.CYAN + colorama.Style.BRIGHT + "Proposed Commands:" + colorama.Style.RESET_ALL)
    for n, command in enumerate(commands):
        print(colorama.Fore.WHITE + colorama.Style.BRIGHT + "-" * 5 + "Command " + str(
            n) + "-" * 5 + colorama.Style.RESET_ALL)
        print()
        print(colorama.Fore.RED + colorama.Style.BRIGHT + command + colorama.Style.RESET_ALL)
        print()

    if len(commands) > 0:
        while True:
            quit_flag = False
            print_menu()
            option = int(input('Choose an option from 1 to 8: '))
            if option == 7:
                print("Write your new prompt")
                break
            if option == 8:
                quit_flag = True
                break
            selected = options.get(option)
            print("You selected option " + str(option))
            if selected:
                selected()
            else:
                print('Invalid option. Try again.')

            print("\n" + "=" * 20 + "\n")

        if quit_flag:
            break