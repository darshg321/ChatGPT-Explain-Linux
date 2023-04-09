#!/usr/bin/python3
import argparse, openai, re, subprocess, os
from sys import stdout, exit


openai.api_key = os.getenv("OPENAI_API_KEY")

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Ask ChatGPT a question, explain output, or find a command for what you want to do')

# Add arguments to the parser
# parser.add_argument('--explain', action='store_true', help='Provide explanation for the last terminal output')
parser.add_argument('--ask', action='store_true', help='Ask any question')
parser.add_argument('--findcommand', '-findcmd', action='store_true', help='Turn english into terminal commands, and run them with a confirmation')
parser.add_argument('prompt', type=str, help='The prompt you want to give')

# Parse the arguments
args = parser.parse_args()

# Check that either --explain or --ask was used
if not (args.ask or args.findcommand):
    parser.error("Either --explain or --ask must be specified.")

# Check that the string argument was provided
if not (args.prompt):
    parser.error("A prompt argument must be provided.")

if openai.api_key == None:
    parser.error("Set api key with:\n`echo 'export OPENAI_API_KEY=YOUR_KEY_HERE' >> ~/.bashrc && source ~/.bashrc` on linux,\nor \
`setx OPENAI_API_KEY YOUR_KEY_HERE /M` on windows, and restart your terminal")

print("You asked:", args.prompt)

def sendPrompt(Prompt):
    print("Asking GPT...")
    if args.ask:
        gptResponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Be a helpful assistant"},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": Prompt}
        ]
    )
    elif args.findcommand:
        gptResponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Give terminal command(s) to do what the prompt says. Do not add alternatives. Use only commands that a shell can run."},
            {"role": "user", "content": "How do I make a text file named test.txt in my current directory?"},
            {"role": "assistant", "content": "You can make a text file named test.txt in your current directory with the command: ```touch test.txt```."},
            {"role": "user", "content": Prompt}
        ],
        temperature=0.2
    )
    
    return gptResponse.choices[0].message.content

def getCommand(originalString: str) -> str:
    pattern = r"```([\s\S]*?)```"  # pattern to match text inside three backticks
    matches = re.findall(pattern, originalString)  # find all matches
    # print(matches)
    if matches:
        commands = [line.strip() for line in matches[0].splitlines()]  # extract commands and remove leading/trailing whitespace
        commands = list(filter(None, commands))  # remove any empty strings from the list
        return commands
    else:
        return []

def runCommand(commands: list):
    # print(type(commands))
    for command in commands:
        print(f"\nExecuting command: {command}")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        if len(result.stdout) > 0:
            print(f"Output: {result.stdout.decode('utf-8')}")

        # Check if the command produced any errors
        if len(result.stderr) > 0:
            print(f"Error: {result.stderr.decode('utf-8')}")
            return

def Main():
    
    gptResponse = sendPrompt(args.prompt)
    print("\n", gptResponse)
    
    if args.findcommand:
        gptCommands = getCommand(gptResponse)
        if not gptCommands:
            print("No commands to run")
            exit(0)

        print("\nCommand(s) to run: ")
        for command in gptCommands:
            print(command)
        print("\nRun command(s)? (Y/n)")

        yesArray = {'yes','y', 'ye', ''}
        noArray = {'no','n'}
        choice = 'jasdbfipub'
        
        choice = input().lower()
        if choice in yesArray:
            runCommand(gptCommands)
        elif choice in noArray:
            exit(0)
        else:
            stdout.write("Please respond with 'yes' or 'no'")
            
Main()
