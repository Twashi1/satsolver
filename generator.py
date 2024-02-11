### EXAMPLE USAGE AT BOTTOM

import random

# each literal has x chance of being included in equation
DEFAULT_LITERAL_PRESENCE_WEIGHT = 0.8
CLAUSE_GENERATION_ATTEMPT_LIMIT = 100

# lazy lambdas
random_sign = lambda x: x * (random.randint(0, 1) * 2 - 1)
gen_literals = lambda count, weight: [random_sign(i + 1) for i in range(count) if random.random() < weight] 

def dimacs(clause_set):
    variableCount = 0
    clauseCount = len(clause_set)
    
    # count variables
    literals = set()

    for clause in clause_set:
        for literal in clause:
            literals.add(abs(literal))

    variableCount = len(literals)

    # yikes
    return f"p cnf {variableCount} {clauseCount}\n" + " 0\n".join([" ".join(clause) for clause in clause_set]) + " 0\n"

# requires a WORKING!! sat solver to see if a case is satisfiable or not
# config specifies clause count and variable count in the following format:
# [(variableCount, clauseCount), ...]
# may generate duplicate clauses
# will not generate empty clauses
def generate(filename, configs, sat_solver, literal_presence_weight = DEFAULT_LITERAL_PRESENCE_WEIGHT, is_simple_sat_solve = False):
    with open("filename", "wt+") as f:
        for i, config in configs:
            # im on 5 hour sleep so alternating snake and camel case fuck it
            variableCount, clauseCount = config

            clause_set = []

            for _ in range(clauseCount):
                clause = gen_literals(variableCount, literal_presence_weight)
                attempts = 0

                while len(clause) == 0 and attempts < CLAUSE_GENERATION_ATTEMPT_LIMIT:
                    clause = gen_literals(variableCount, literal_presence_weight)
                    attempts += 1

                if attempts >= CLAUSE_GENERATION_ATTEMPT_LIMIT:
                    raise RuntimeError("Failed to generate a clause in 100 attempts, bad literal presence weight?")

                # duplicates allowed because cba
                # no empty clauses allowed
                clause_set.append(clause)

            is_satisfiable = None

            if is_simple_sat_solve:
                is_satisfiable = sat_solver(clause_set) is not False
            else:
                is_satisfiable = sat_solver(clause_set, []) is not False

            word = 'satisfiable' if is_satisfiable else 'unsatisfiable'

            # format it
            f.write(f"# {i + 1}. {word}\n{dimacs(clause_set)}\n")

# both intervals inclusive
def generateConfigs(count, variableInterval, clauseInterval):
    return [
        (random.randint(*variableInterval), random.random(*clauseInterval))
        for _ in range(count)
    ]


# import your own [WORKING!!!] implementation here (and remove these three lines)
import sys
sys.path.append("/secret/")
import implementation

generate(
    "tests/cooltest.txt",
    generateConfigs(1000, (3, 5), (1, 3)),  # 1k cases, with 3-5 variables and 1-3 clauses
    None                                    # your sat solve function, e.g. impementation.dpll_sat_solve
)