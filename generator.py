### EXAMPLE USAGE AT BOTTOM
import random

# TODO: with low variable counts and clause counts (esp) there are few unsatisfiable cases
#       just because random chance

# TODO: this code sucks someone fix it all for me :) (you can put it in learning log for progblock cw no?)

# each literal has x chance of being included in equation
DEFAULT_LITERAL_PRESENCE_WEIGHT = 0.8
CLAUSE_GENERATION_ATTEMPT_LIMIT = 100
# if set to true, then we say the variable count is just how many unique (absolute value) literals there are
# if set to false, we just take the absolute value of largest value literal as variable count
STRICTLY_UNQIUE_VARIABLE_COUNT = True

# lazy lambdas
random_sign = lambda x: x * (random.randint(0, 1) * 2 - 1)
gen_literals = lambda count, weight: [random_sign(i + 1) for i in range(count) if random.random() < weight] 

# TODO: issues with this, generating bad format
def dimacs(clause_set):
    variableCount = 0
    clauseCount = len(clause_set)
    
    # count variables
    literals = set()

    for clause in clause_set:
        for literal in clause:
            literals.add(abs(literal))

    variableCount = len(literals) if STRICTLY_UNQIUE_VARIABLE_COUNT else max(literals)

    # yikes
    return f"p cnf {variableCount} {clauseCount}\n" + " 0\n".join([" ".join([str(literal) for literal in clause]) for clause in clause_set]) + " 0\n"

# requires a WORKING!! sat solver to see if a case is satisfiable or not
# config specifies clause count and variable count in the following format:
# [(variableCount, clauseCount), ...]
# may generate duplicate clauses
# will not generate empty clauses
def generate(filename, configs, sat_solver, literal_presence_weight = DEFAULT_LITERAL_PRESENCE_WEIGHT, is_simple_sat_solve = False):
    with open(filename, "w+") as f:
        for i, config in enumerate(configs):
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
            s = f"# {i + 1} {word}\n{dimacs(clause_set)}\n"

            f.write(s)

# both intervals inclusive
def generateConfigs(count, variableInterval, clauseInterval):
    return [
        (random.randint(*variableInterval), random.randint(*clauseInterval))
        for _ in range(count)
    ]


# import your own [WORKING!!!] implementation here (and remove these three lines)
import sys
sys.path.append("secret/")
import implementation

generate(
    "tests/cooltest.txt",
    generateConfigs(30, (2, 2), (2, 7)),    # n cases, with a-b variables and c-d clauses
    implementation.simple_sat_solve,        # your sat solve function, e.g. impementation.dpll_sat_solve
    DEFAULT_LITERAL_PRESENCE_WEIGHT,
    True                                    # turn off unless using simple sat solve
)