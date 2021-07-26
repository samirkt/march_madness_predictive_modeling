from models import rf, lr, nn
from utils.globs import *
import pandas as pd
import numpy as np


def main():
    table = pd.read_csv(tourney_ref,index_col=False)

    # Call model training methods
    nn(table.copy())
    rf(table.copy())
    lr(table.copy())

if __name__ == "__main__":
    main()

