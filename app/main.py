import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ui.web_interface import render

if __name__ == "__main__":
    render()
