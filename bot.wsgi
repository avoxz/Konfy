import sys
import os

project_home = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_home)

from bot import app

application = app
