"""
ADK Triage Agent Main Module

This is the main entry point for the ADK Triage Agent application.
"""
from agent import run_agent_interactive

def main():
    """Main function to run the triage agent."""
    print("Starting ADK Triage Agent...")
    run_agent_interactive()


if __name__ == "__main__":
    main()