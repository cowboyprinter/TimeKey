# (Assuming this is part of your existing my_cli.py or a similar file)

# Store your command descriptions in a dictionary for easy access
COMMANDS_HELP = {
    "hello": "Prints a simple greeting.",
    "greet <name>": "Greets the specified person.",
    "add <num1> <num2>": "Adds two numbers together.",
    "config <setting> [--value <val>] [--show]": "Configures or shows a setting (example, needs implementation).",
    # --- Add your new Quantum Time Math commands here ---
    "define_mnode <id> [data]": "Defines a Moment-Node (M-Node) with an ID and optional data. (QTM)",
    "link_mnodes <id1> <id2> <relationship>": "Links two M-Nodes with a temporal relationship (e.g., 'before', 'after_potential'). (QTM)",
    "help": "Shows this help message.",
    "exit": "Exits the CLI."
}

def show_help():
    print("\nAvailable commands:")
    print("-------------------")
    for command, description in COMMANDS_HELP.items():
        print(f"  {command:<40} - {description}") # Adjust spacing as needed
    print("\n(QTM) indicates a Quantum Time Math related command.")
    print("Type a command followed by its arguments, if any.\n")

# ... (your existing process_command and main functions)

def process_command(command_input):
    parts = command_input.strip().split()
    if not parts:
        return

    command_name = parts[0].lower()
    args = parts[1:]

    if command_name == "help":
        show_help()
    elif command_name == "hello":
        print("Hello there, user!")
    elif command_name == "greet":
        if args:
            print(f"Greetings, {' '.join(args)}!")
        else:
            print("Usage: greet <name>")
    # ... other commands ...
    # --- Your Quantum Time Math command handling will go here ---
    elif command_name == "define_mnode":
        if len(args) >= 1:
            mnode_id = args[0]
            mnode_data = " ".join(args[1:]) if len(args) > 1 else "No data"
            # In a real app, you'd store this in your PAGE structure
            print(f"QuantumTimeCLI: Defined M-Node '{mnode_id}' with data: '{mnode_data}'")
            print(f"  (Conceptual PAGE location: O?- :: D!-[{mnode_id}] ({mnode_data}))")
        else:
            print("Usage: define_mnode <id> [data]")

    elif command_name == "link_mnodes":
        if len(args) == 3:
            mnode_id1, mnode_id2, relationship = args[0], args[1], args[2]
            # In a real app, you'd update your PAGE structure
            print(f"QuantumTimeCLI: Linking M-Node '{mnode_id1}' to '{mnode_id2}' with relationship '{relationship}'")
            print(f"  (Conceptual T-Path: M-Node[{mnode_id1}] --({relationship})--> M-Node[{mnode_id2}])")
        else:
            print("Usage: link_mnodes <id1> <id2> <relationship>")

    elif command_name == "exit":
        print("Exiting QuantumTimeCLI. Goodbye!")
        return "exit_program"
    else:
        print(f"Unknown command: '{command_name}'. Type 'help' for available commands.")

# ... (your main function that calls process_command in a loop)
def main():
    print("Welcome to chronoscript! Type 'help' for commands. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("QTimeCLI> ") # Changed prompt
            result = process_command(user_input)
            if result == "exit_program":
                break
        except KeyboardInterrupt:
            print("\nExiting QuantumTimeCLI (Ctrl+C). Goodbye!")
            break
        except EOFError:
            print("\nExiting QuantumTimeCLI (EOF). Goodbye!")
            break

if __name__ == "__main__":
    main()