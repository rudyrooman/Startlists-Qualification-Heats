# -*- coding: utf-8 -*-
from itertools import combinations
from random import sample
from sys import exit
from timeit import default_timer
from collections import Counter

from openpyxl import load_workbook
from ortools.linear_solver import pywraplp
import numpy as np
import pandas as pd


class Runner:
    def __init__(self):
        self.ID = 0
        self.FED = ''
        self.Surname = ''
        self.Firstname = ''
        self.StartGrp = 0
        self.RankingPoints = 0
        self.Rank = 0
        self.Heat = 0
        self.Time = 0

    def __str__(self):
        return f"{self.Firstname} {self.Surname}"


class Nation:
    def __init__(self, fed):
        self.FED = fed
        self.runners = []
        self.count = 0
        self.groupcount = [0, 0, 0, 0]

    def count_runners(self, all_runners):
        self.runners = [r for r in all_runners if self.FED == r.FED]
        self.count = len(self.runners)

        # Efficiënte telling via Counter i.p. side loops
        start_grp_counts = Counter(r.StartGrp for r in self.runners)
        for i in range(4):
            self.groupcount[i] = start_grp_counts[i]

    def __str__(self):
        return str(self.FED)


def find_heats_time(_runners, _heats, _nations, _z):
    solver = pywraplp.Solver('SolveAssignmentProblemMIP', pywraplp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING)
    if not solver:
        print("Solver niet beschikbaar.")
        return None, "FAILED"

    # Verdeel lopers over heats met numpy
    runners_per_heat = [len(it) for it in np.array_split(range(len(_runners)), _heats)]

    # Bereken starting blocks
    block_counts = Counter(r.StartGrp for r in _runners)
    starting_blocks = [block_counts[sb] for sb in range(4)]

    # Voeg lopers zonder voorkeur (0) toe aan de kleinste groep (1, 2 of 3)
    min_index = starting_blocks[1:].index(min(starting_blocks[1:])) + 1
    starting_blocks[min_index] += starting_blocks[0]
    starting_blocks = starting_blocks[1:]

    print('\n...Optimizer is running...Please wait...\n')

    # [ START Variabelen aanmaken ]
    match = {}
    for _r in _runners:
        for _h in range(1, _heats + 1):
            for _t in range(runners_per_heat[_h - 1]):
                match[_r, _h, _t] = solver.BoolVar(f'match[{_r.ID},{_h},{_t}]')

    # [ START Restricties ]
    # 1. Elke loper exact 1 heat/tijd combinatie
    for _r in _runners:
        solver.Add(solver.Sum([match[_r, _h, _t] for _h in range(1, _heats + 1)
                               for _t in range(runners_per_heat[_h - 1])]) == 1)

    # 2. Elke heat/tijd combinatie exact 1 loper
    for _h in range(1, _heats + 1):
        for _t in range(runners_per_heat[_h - 1]):
            solver.Add(solver.Sum([match[_r, _h, _t] for _r in _runners]) == 1)

    # 3. Balanceer lopers van hetzelfde land over de heats
    for _n in _nations:
        for _h in range(1, _heats + 1):
            solver.Add(solver.Sum([match[_r, _h, _t] for _t in range(runners_per_heat[_h - 1]) for _r in _n.runners])
                       <= (1 + (_n.count - 1) // _heats))
            solver.Add(solver.Sum([match[_r, _h, _t] for _t in range(runners_per_heat[_h - 1]) for _r in _n.runners])
                       >= (_n.count // _heats))

    # 4. Spreiding op basis van ranking (groepen van grootte van aantal heats)
    _runners2 = _runners[:(len(_runners) // _heats) * _heats]
    for group in [list(it) for it in np.array_split(_runners2, len(_runners) // _heats)]:
        for _h in range(1, _heats + 1):
            solver.Add(solver.Sum([match[_r, _h, _t] for _r in group for _t in range(runners_per_heat[_h - 1])]) == 1)

    # 5. Opeenvolgende tijden niet van hetzelfde land
    for _n in _nations:
        for _r1, _r2 in combinations(_n.runners, 2):
            for _h in range(1, _heats + 1):
                for _t in range(runners_per_heat[_h - 1] - 1):
                    solver.Add(match[_r1, _h, _t] + match[_r2, _h, _t + 1] <= 1)

    # 6. Startgroep voorkeuren (met relaxatie factor _z)
    for _r in _runners:
        if _r.StartGrp > 1:
            solver.Add(solver.Sum([match[_r, _h, _t] * _t for _h in range(1, _heats + 1)
                                   for _t in range(runners_per_heat[_h - 1])]) >=
                       ((sum(starting_blocks[0:_r.StartGrp - 1]) - 1) // _heats - _z))
        if _r.StartGrp < _heats and _r.StartGrp != 0:
            solver.Add(solver.Sum([match[_r, _h, _t] * _t for _h in range(1, _heats + 1)
                                   for _t in range(runners_per_heat[_h - 1])]) <=
                       ((sum(starting_blocks[0:_r.StartGrp]) - 1) // _heats + _z))

    # 7. Fixeer willekeurige lopers voor random startlijst
    random_runners = sample(_runners, _heats)
    for _h, _r in enumerate(random_runners, start=1):
        solver.Add(solver.Sum([match[_r, _h, _t] for _t in range(runners_per_heat[_h - 1])]) == 1)

    sol = solver.Solve()

    if sol == solver.OPTIMAL:
        if _z == 0:
            print('Starting times: Optimal solution found\n')
        else:
            print(f'Starting times: Solution found with correction factor = {_z}\n')

        print(f'runners per heat: {runners_per_heat}\n')
        print(f'runners per starting block: {starting_blocks}\n')
        print('Following runners are fixed to a heat to ensure random startlists.')
        for _c, _r in enumerate(random_runners, start=1):
            print(f'{_r} to heat {_c}.')
        print()

        for _h in range(1, _heats + 1):
            for _r in _runners:
                for _t in range(runners_per_heat[_h - 1]):
                    if match[_r, _h, _t].solution_value() == 1:
                        _r.Heat = _h
                        _r.Time = _t
        return solver, 'OPTIMAL'

    return solver, 'FAILED'


# ### PROGRAMMA START HIER ### #

print('###################################################')
print('##### STARTLISTS TOOL with LINEAR PROGRAMMING #####')
print('###################################################')
print()

heats = 3
runners = []
nations = []
start_time = default_timer()

# Inlezen data
wb = load_workbook(filename='LP_start_entries.xlsx', data_only=True)
sheet1 = wb.active

teller = 5
while sheet1.cell(row=teller, column=1).value:
    runner = Runner()
    runner.ID = sheet1.cell(row=teller, column=1).value
    runner.FED = sheet1.cell(row=teller, column=2).value
    runner.Surname = sheet1.cell(row=teller, column=3).value
    runner.Firstname = sheet1.cell(row=teller, column=4).value
    runner.StartGrp = sheet1.cell(row=teller, column=5).value
    runner.RankingPoints = sheet1.cell(row=teller, column=6).value

    runners.append(runner)  # Handmatig toevoegen ipv via side-effect constructor
    teller += 1

# Aanmaken landen-instanties
unique_feds = list(dict.fromkeys([r.FED for r in runners]))
for country in unique_feds:
    n = Nation(country)
    n
    nations.append(n)

for n in nations:
    n.count_runners(runners)

print('Startgroup Validation\n')
startgrouperror = False

# Validaties
unexpected = [r.StartGrp for r in runners if r.StartGrp not in [0,1,2,3]]
if unexpected:
    startgrouperror = True
    print('Among startgroup entries we found following unexpected data: ', end='')
    print(*unexpected, sep=", ")

grp0runners = [r for r in runners if r.StartGrp == 0]
if grp0runners:
    startgrouperror = True
    print(f'Currently you have {len(grp0runners)} runners without startgroup or startgroup 0.')

for n in nations:
    for i in range(1, 4):
        if n.groupcount[i] > 1 + (n.count - 1) // 3:
            print(f'Too many runners from {n.FED} in startgroup {i}')
            startgrouperror = True

if startgrouperror:
    print('\nWe strongly recommend to correct startgroups before proceeding.')
    print('Type "s" and enter to stop program or "p" to proceed: ', end='')
    answer = ''
    while answer not in ['p', 's']:
        answer = input().strip().lower()
    if answer == 's':
        exit()
else:
    print('Startgroup Validation completed without comments.\n')

# Sorteren op basis van ranking
runners = sorted(runners, key=lambda x: x.RankingPoints, reverse=True)
print(f'We have {len(runners)} entries.')

for index, r in enumerate(runners, start=1):
    r.Rank = index

# Optimalisatie-loop met veiligheidslimiet tegen oneindige loops
z = 0
max_z = 50
while z < max_z:
    solution, optimal_result = find_heats_time(runners, heats, nations, z)
    if optimal_result == 'OPTIMAL':
        break
    z += 1
else:
    print(f"Fout: Geen oplossing gevonden binnen een relaxatie van z={max_z}. Programma gestopt.")
    exit()

print('Making startlists.xlsx')
runners = sorted(runners, key=lambda x: (x.Heat, x.Time))

# Console output behouden voor de gebruiker
for r in runners:
    print(r.Heat, r.Time, r, r.FED, r.Rank, r.ID, sep=";")

# Slimmer & sneller exporteren met Pandas DataFrame naar Excel
dfver = pd.DataFrame([vars(r) for r in runners])

# Kolomvolgorde netjes structureren voor de startlijst sheet
columns_order = ['Heat', 'Time', 'Firstname', 'Surname', 'FED', 'Rank', 'RankingPoints', 'ID', 'StartGrp']
df_excel = dfver[columns_order]

# Schrijf direct naar Excel (overschrijft/maakt bestand aan)
df_excel.to_excel('startlists.xlsx', index=False, sheet_name='startlist')

elapsed = default_timer() - start_time
print(f'\nCalculation time: {round(elapsed, 3)} seconds.')

#
# Verificaties (Pandas)
#
print("\n" + "*" * 18)
print("Number of runners per federation & startgroup")
print(dfver.groupby(['FED', 'StartGrp']).size().to_frame(name='Count'))

print("\n" + "*" * 18)
print("Number of runners per federation & heat")
print(dfver.groupby(['FED', 'Heat']).size().to_frame(name='Count'))

print("\n" + "*" * 18)
print("Number of runners per federation & heat - min, max and diff")
runnersperheat = dfver.groupby(['FED', 'Heat']).size().to_frame(name='Count')
t = runnersperheat.groupby('FED')['Count'].agg([('Min', 'min'), ('Max', 'max')])
t['Diff'] = t['Max'] - t['Min']
print(t)

print("\n" + "*" * 18)
