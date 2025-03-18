import os
import mm_modeling as mm

mm_path = os.path.dirname(mm.__file__)

FIRST_YEAR = 2024
DATA_DIR = os.path.join(mm_path, "data")
TRAIN_DATA_DIR = os.path.join(DATA_DIR, "train_data")