### EXAMPLE USAGE AT BOTTOM
import random

# TODO: this code sucks someone fix it all for me :) (you can put it in learning log for progblock cw no?)

# Each literal has x chance of being included in a given clause
# If this is not 1, its possible a literal isn't generated in any clause, thus we get less than the requested minimum
#   number of variables
DEFAULT_LITERAL_PRESENCE_WEIGHT = 0.8
# Attempts to generate a clause before we assume that the given arguments do not allow generation of any valid clause
#   or that valid clauses are too rare
CLAUSE_GENERATION_ATTEMPT_LIMIT = 100

# Give variable x a random sign
random_sign = lambda x: x * (random.randint(0, 1) * 2 - 1)
# Generate literals for a given clause
gen_literals = lambda count, weight: [random_sign(i + 1) for i in range(count) if random.random() < weight] 

# TODO: would be nice if past Thomas told me what was wrong with it
# TODO: issues with this, generating bad format
def dimacs(clause_set):    
    # Count variables
    literals = set()

    for clause in clause_set:
        for literal in clause:
            literals.add(abs(literal))

    # Missing some variable in every clause, need to
    #   rename the variables
    if len(literals) != max(literals):
        # So we can use index
        literals = list(literals)

        # TODO: almost definitely an inefficient way of doing this
        for clause in clause_set:
            for i, variable in enumerate(clause):
                clause[i] = ((variable > 0) * 2 - 1) * (literals.index(abs(variable)) + 1)

    variableCount = len(literals)
    clauseCount = len(clause_set)

    # yikes
    return f"p cnf {variableCount} {clauseCount}\n" + " 0\n".join([" ".join([str(literal) for literal in clause]) for clause in clause_set]) + " 0\n"

def generateClauseSet(config, literal_presence_weight):
    variableCount, clauseCount = config

    clause_set = []

    for _ in range(clauseCount):
        attempts = 0

        clause = gen_literals(variableCount, literal_presence_weight)

        while len(clause) == 0 and attempts < CLAUSE_GENERATION_ATTEMPT_LIMIT:
            clause = gen_literals(variableCount, literal_presence_weight)

            attempts += 1

        if attempts >= CLAUSE_GENERATION_ATTEMPT_LIMIT:
            raise RuntimeError(f"Failed to generate a clause in {attempts} attempts, bad literal presence weight?")
        
        clause_set.append(clause)

    return clause_set


# Requires a WORKING sat solver to label a case as satisfiable or not
# configs specifies clause count and variable count in the following format:
#   [(variableCount, clauseCount), ...]
# Will generate duplicate clauses sometimes
# will not generate empty clauses
def generate(filename, configs, sat_solver, literal_presence_weight = DEFAULT_LITERAL_PRESENCE_WEIGHT, is_simple_sat_solve = False):
    with open(filename, "w+") as f:
        for i, config in enumerate(configs):
            clause_set = generateClauseSet(config, literal_presence_weight)

            is_satisfiable = None

            if is_simple_sat_solve:
                is_satisfiable = sat_solver(clause_set) is not False
            else:
                is_satisfiable = sat_solver(clause_set, []) is not False

            word = 'satisfiable' if is_satisfiable else 'unsatisfiable'

            # format it
            s = f"# {i + 1} {word}\n{dimacs(clause_set)}\n"

            f.write(s)

# Both intervals inclusive
# Not guaranteed to generate the minimum of the variableInterval
def generateConfigs(count, variableInterval, clauseInterval):
    return [
        (random.randint(*variableInterval), random.randint(*clauseInterval))
        for _ in range(count)
    ]

# import your own [WORKING] implementation here (and remove these three lines)
import sys
sys.path.append("secret/")
import implementation

generate(
    "tests/ntest.txt",
    generateConfigs(1000, (3, 3), (4, 4)),  # n cases, with a-b variables and c-d clauses
    implementation.simple_sat_solve,        # your known working sat-solve function
    DEFAULT_LITERAL_PRESENCE_WEIGHT,
    True                                    # False unless using simple sat solve
)