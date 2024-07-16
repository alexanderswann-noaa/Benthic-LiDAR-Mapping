import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(current_dir, "..", "build", "CloudComPy310", "CloudCompare")
target_dir = os.path.normpath(target_dir)
sys.path.append(target_dir)