from utils.brackets import brackets
from datetime import datetime as dt
from copy import copy

import numpy as np
import pandas as pd

year = dt.now().year

b = brackets[year]
b = [name for name,seed in b]
p = {name: 1 for name in b}

mat = pd.read_csv('matchup_mat.csv')
schools = mat.columns.values[1:]
pair_probs = mat.to_numpy()[:,1:]

lookup = {}
for num1, school1 in enumerate(schools):
    opp = {} 
    for num2, school2 in enumerate(schools):
        if school1 == school2: continue
        p1 = pair_probs[num1][num2]
        p2 = 1-pair_probs[num2][num1]
        if p1 == -1 or p2 == -1:
            print("ERROR: unexpected -1")
            quit()
        opp[school2] = np.mean([p1,p2])
    lookup[school1] = opp



rkeys = ["r64", "r32", "r16", "r8", "r4", "r2","r1"]

rounds = {
        "r64": np.reshape(b,(64,1)),
        "r32": np.reshape(b,(32,2)),
        "r16": np.reshape(b,(16,4)),
        "r8": np.reshape(b,(8,8)),
        "r4": np.reshape(b,(4,16)),
        "r2": np.reshape(b,(2,32)),
        "r1": np.reshape(b,(1,64)),
    }

probs = {
        "r64": p,
        "r32": p,
        "r16": p,
        "r8": p,
        "r4": p,
        "r2": p,
        "r1": p,
    }


def calc(rounds, r_ind, probs, p):
    prev_round = rkeys[r_ind-1]
    curr_round = rkeys[r_ind]
    prev_probs = probs[prev_round].copy()
    curr_probs = probs[curr_round].copy()

    prev_groups = {}
    for group in rounds[prev_round]:
        for t in group:
            prev_groups[t] = group

    for group in rounds[curr_round]:
        for t in group:
            prob = prev_probs[t]
            cum_prob = 0
            for t2 in group:
                if t2 not in prev_groups[t]:
                    cum_prob += lookup[t][t2]*prev_probs[t2]
            cum_prob *= prob
            curr_probs[t] = cum_prob

    return curr_probs



for i in range(1,len(rkeys)):
    probs_update = calc(rounds, i, probs, p)
    probs[rkeys[i]] = probs_update.copy()


seen = set()
results = {}
for i in range(len(rkeys))[::-1]:
    r = rkeys[i]
    winners = []
    for group in rounds[r]:
        max_p = ("", -1)
        for t in group:
            if t in seen:
                max_p = (t, probs[r][t])
                break
            if probs[r][t] > max_p[1]:
                max_p = (t, probs[r][t])
        winners.append(max_p[0])
        seen.add(max_p[0])
    results[r] = winners


# Display results
for i in range(1,len(rkeys)):
    print("--- {0} ---".format(rkeys[i-1]))
    for w in results[rkeys[i]]:
        print(w)
        _ = input()
    print()

