# TermGPT
Giving LLMs like GPT-4 the ability to plan and execute terminal commands

Video explanation and usage examples: https://youtu.be/O4EmRi0_CI4

The notebook also breaks down how the script works.

# Usage

Run with `$ python3 TermGPT.py`
You will need to create a `.env` file similar to https://github.com/Sentdex/TermGPT/blob/main/.env.example, or set `OPENAI_API_KEY` manually.

From here, you make your programming/development request. The script will run and query GPT-4 for a series of terminal commands to run to achieve this objective. This is including, but not limited to: reading files, writing code, reading websites, running code, running terminal commands...etc. 

The proposed commands are stored to a list and then presented back to the user again in bold red text, prior to running. After reviewing these commands, you can opt to run them, or not.

# Future work

- I would like to primarily find an open source model that can yield similar performance to GPT-4 in this realm.
- Simplify and add more natural language. Most likely, starting "prompts" will need higher and lower level understanding. Rather than doing something like --r [FILENAME], I would like to have a higher level pass via the LLM to determine if any files should be read, allowing for a pure "natural language" approach, along with likely far more generalization.
