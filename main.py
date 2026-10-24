"""
main.py - Application Entry Point
---------------------------------
Project Title: "AI Requirement Validator for Software Development"
Purpose: College Minor Project

Entry point for launching the AI Requirement Validator desktop GUI.
"""

import sys
import gui

def main():
    """Starts the Tkinter desktop application."""
    try:
        gui.launch_app()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
        sys.exit(0)
    except Exception as error:
        print(f"\n[Fatal Error] Could not launch application: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
