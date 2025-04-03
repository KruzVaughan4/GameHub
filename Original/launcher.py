import os
import sys
from subprocess import call

# Path to the virtual environment
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'Scripts', 'python.exe')

# Ensure the correct python interpreter from the virtual environment is used
call([venv_path] + sys.argv[1:])
