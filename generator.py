# Configure and run at bottom
# Some global variables to edit just below

import random

# TODO: this code sucks someone fix it all for me :) (you can put it in learning log for progblock cw no?)
# TODO: using literal when variable is meant in some places

# Each literal has x chance of being included in a given clause
# If this is not 1, its possible a literal isn't generated in any clause, thus we get less than the requested minimum
#   number of variables
LITERAL_PRESENCE_WEIGHT = 0.8
# Attempts to generate a clause before we assume that the given arguments do not allow generation of any valid clause
#   or that valid clauses are too rare
CLAUSE_GENERATION_ATTEMPT_LIMIT = 100
# Ensures all variables in range 1->n are generated (where n is variableCount)
#   Note this does not necessarily mean it will always generate as many variables as specified in the config
#   especially at low literal presence weights
NO_MISSING_VARIABLES = False

# Give variable x a random sign
random_sign = lambda x: x * (random.randint(0, 1) * 2 - 1)
# Generate a clause with a given number of literals
generate_clause = lambda count: [random_sign(i + 1) for i in range(count) if random.random() < LITERAL_PRESENCE_WEIGHT] 

# TODO: would be nice if past Thomas told me what was wrong with it
# TODO: issues with this, generating bad format
def dimacs_string(clause_set):    
    # Count variables
    literals = set()

    for clause in clause_set:
        for literal in clause:
            literals.add(abs(literal))

    variable_count = max(literals)
    clause_count = len(clause_set)

    # yikes
    return f"p cnf {variable_count} {clause_count}\n" + " 0\n".join([" ".join([str(literal) for literal in clause]) for clause in clause_set]) + " 0\n"

def generate_clause_set(config):
    variableCount, clauseCount = config

    clause_set = []

    for _ in range(clauseCount):
        attempts = 0

        clause = generate_clause(variableCount)

        while len(clause) == 0 and attempts < CLAUSE_GENERATION_ATTEMPT_LIMIT:
            clause = generate_clause(variableCount)

            attempts += 1

        if attempts >= CLAUSE_GENERATION_ATTEMPT_LIMIT:
            raise RuntimeError(f"Failed to generate a clause in {attempts} attempts, bad literal presence weight?")
        
        clause_set.append(clause)

    if NO_MISSING_VARIABLES:
        # Re-assign literals to ensure we fit the range [1, n]
        # So we can use index
        literals = list({abs(literal) for clause in clause_set for literal in clause})

        if len(literals) != max(literals):
            # TODO: almost definitely an inefficient way of doing this
            for clause in clause_set:
                for i, variable in enumerate(clause):
                    clause[i] = ((variable > 0) * 2 - 1) * (literals.index(abs(variable)) + 1)

    return clause_set


# Requires a WORKING sat solver to label a case as satisfiable or not
# 'configs' specifies clause count and variable count in the following format:
#   [(variableCount, clauseCount), ...]
# Will generate duplicate clauses sometimes
# Will not generate empty clauses
# Will not generate two conflicting literals in the same clause (-1, 1, 2)
def generate(filename, configs, sat_solver, is_simple_sat_solve = False):
    with open(filename, "w+") as f:
        for i, config in enumerate(configs):
            clause_set = generate_clause_set(config)

            is_satisfiable = None

            if is_simple_sat_solve:
                is_satisfiable = sat_solver(clause_set) is not False
            else:
                is_satisfiable = sat_solver(clause_set, []) is not False

            word = 'satisfiable' if is_satisfiable else 'unsatisfiable'

            # format it
            s = f"# {i + 1} {word}\n{dimacs_string(clause_set)}\n"

            f.write(s)

# Both intervals inclusive
# Not guaranteed to generate the minimum of the variable_interval
def generate_configs(count, variable_interval, clause_interval):
    return [
        (random.randint(*variable_interval), random.randint(*clause_interval))
        for _ in range(count)
    ]

# Import your own [WORKING] implementation here (and remove these three lines)
import sys
sys.path.append("secret/")
import implementation

generate(
    "tests/ntest.txt",
    generate_configs(1000, (3, 3), (4, 4)),  # n cases, with a-b variables and c-d clauses
    implementation.simple_sat_solve,        # your known working sat-solve function
    True                                    # False unless using simple sat solve
)