from models import rf, lr, nn
import pandas as pd
import numpy as np


def main():
    table = pd.read_csv("train_data/tourney-0.9-0-1993-2021.csv",index_col=False)
    #print(len(np.array(table)[0]))

    nn(table.copy())
    #rf(table.copy())
    #lr(table.copy())

if __name__ == "__main__":
    main()

