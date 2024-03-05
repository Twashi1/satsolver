# TODO: attempt to ensure unsatisfiable cases by inverting satisfying truth assignments

import random
import time
from dataclasses import dataclass
from inspect import signature

# Importing implementation from a folder called "secret"
import sys
sys.path.append("secret/")
import implementation

### Set options here

# Each literal has x chance of being included in a given clause
# If this is not 1, its possible a literal isn't generated in any clause, thus we get less than the requested minimum
#   number of variables
LITERAL_PRESENCE_WEIGHT = 0.8
# Attempts to generate a clause before we assume that the given arguments do not allow generation of any valid clause
#   or that valid clauses are too rare
CLAUSE_GENERATION_ATTEMPT_LIMIT = 100
# Ensures all variables in range 1->n are generated (where n is variableCount)
#   - Does not necessarily mean it will always generate as many variables as specified in the config
#       especially at low literal presence weights
NO_MISSING_VARIABLES = False
# Ensures generator never generates empty clause
ALLOW_EMPTY_CLAUSES = True

## GENERATE VARIABLES

# The filename to save the test cases to
GENERATE_FILENAME = "tests/5_big_cases.txt"
# Seed for generation
#   - Might be best to set this to a constant for speed comparisons with testing on the fly
GENERATE_SEED = time.time()
# The interval for how many variables can generate (inclusive)
#   - Not guaranteed to generate the minimum number of variables listed
GENERATE_VARIABLE_INTERVAL = (10, 20)
# The interval for how many clauses can generate (inclusive)
GENERATE_CLAUSE_INTERVAL = (300, 400)
# Generate at most n cases
GENERATE_NUMBER = 500
# Amount of times we attempt to generate a clause before we give up
GENERATE_CLAUSE_ATTEMPT_LIMIT = 1_000
# A working implementation of your SAT solver
#   - Only required for generating your own cases (can keep as None otherwise)
IMPLEMENTATION_WORKING_SAT_SOLVER = implementation.simple_sat_solve

## TEST VARIABLES

# The filename to read the test cases from
TEST_FILENAME = "tests/1k_less_vars_less_clauses.txt"
# The filename to write results of failed tests to
TEST_RESULT_FILENAME = "tests/results.txt"
# The implementation of your SAT solver you want to test
#   - Only required for testing a SAT solver, not generating your own cases
IMPLEMENTATION_TEST_SAT_SOLVER = implementation.dpll_sat_solve
# The implementation of your DIMACS reader
#   - Only required for testing a SAT solver on a file
IMPLEMENTATION_LOAD_DIMACS = implementation.load_dimacs
# The place to temporarily write text to
TEST_TEMPORARY_WRITE_FILENAME = "temp.txt"

## TEST ON FLY VARIABLES
# Requires:
# - GENERATE_FILENAME
# - GENERATE_VARIABLE_INTERVAL
# - GENERATE_CLAUSE_INTERVAL
# - GENERATE_NUMBER
# - GENERATE_CLAUSE_ATTEMPT_LIMIT
# - TEST_RESULT_FILENAME
# - IMPLEMENTATION_WORKING_SAT_SOLVER
# - IMPLEMENTATION_TEST_SAT_SOLVER

def get_variables(clause_set : list[list[int]]) -> set[int]:
    return {abs(literal) for clause in clause_set for literal in clause}

@dataclass
class Case:
    clause_set : list[list[int]]
    is_satisfiable : bool
    name : str

def sanitise_clause_set(clause_set) -> int:
    variables = list(get_variables(clause_set))

    if NO_MISSING_VARIABLES:
        if len(variables) != max(variables):
            # TODO: almost definitely an inefficient way of doing this
            for clause in clause_set:
                for i, literal in enumerate(clause):
                    clause[i] = ((literal > 0) * 2 - 1) * (variables.index(abs(literal)) + 1)

    # DIMACS format always lists the largest variable in the solution
    return max(variables)

def convert_to_dimacs(case : Case) -> str:
    variable_count = sanitise_clause_set(case.clause_set)
    clause_count = len(case.clause_set)
    satisfiability = 'sat' if case.is_satisfiable else 'unsat'

    return f"c special {satisfiability} \"{case.name}\"\np cnf {variable_count} {clause_count}\n" + " 0\n".join([" ".join([str(literal) for literal in clause]) for clause in case.clause_set]) + " 0\n"

def write_cases(cases, filename) -> None:
    cases = list(cases)
    
    if len(cases) == 0: return

    with open(filename, "wt+") as f:
        for case in cases:
            f.write(convert_to_dimacs(case))

def generate_clause() -> list[int]:
    return [
        (i + 1) * (random.randint(0, 1) * 2 - 1)
        for i in range(random.randint(*GENERATE_VARIABLE_INTERVAL))
        if random.random() < LITERAL_PRESENCE_WEIGHT
    ]

def execute_sat_solver(clause_set, solver):
    if solver is None:
        raise RuntimeError("Didn't provide a SAT solver function, check options at top of the file")

    sig = signature(solver)

    if len(sig.parameters) == 1:
        return solver(clause_set)
    else:
        return solver(clause_set, [])

def is_valid(clause : list[int]) -> bool:
    if not ALLOW_EMPTY_CLAUSES:
        if len(clause) == 0: return False

    # TODO: look for duplicate clauses
    # NOTE: I know this could just be "return len(clause)"
    
    return True

def generate_case(name) -> Case:
    clause_count = random.randint(*GENERATE_CLAUSE_INTERVAL)
    clause_set = [None] * clause_count

    for index in range(clause_count):
        clause = generate_clause()
        attempts = 0

        while not is_valid(clause) and attempts < GENERATE_CLAUSE_ATTEMPT_LIMIT:
            clause = generate_clause()

            attempts += 1

        if attempts < GENERATE_CLAUSE_ATTEMPT_LIMIT:
            clause_set[index] = clause

    sanitise_clause_set(clause_set)

    return Case(
        clause_set=clause_set,
        is_satisfiable=execute_sat_solver(clause_set, IMPLEMENTATION_WORKING_SAT_SOLVER) is not False,
        name=name
    )

def write_and_load(text):
    if len(text) == 0: return text

    with open(TEST_TEMPORARY_WRITE_FILENAME, "wt+") as f:
        f.write(text)

    return IMPLEMENTATION_LOAD_DIMACS(TEST_TEMPORARY_WRITE_FILENAME)

def read_dimacs():
    cases = []

    with open(TEST_FILENAME, "r") as f:
        # TODO: don't assume newline
        next_line_expect_info = False

        current_case = Case(None, None, None)
        current_text = ""

        for line in f.readlines():
            if line.startswith("c special"):
                current_case.clause_set = write_and_load(current_text)
                cases.append(current_case)

                _, _, satisfiability, name = line.split(" ")

                current_case = Case(None, satisfiability == "sat", name)
                current_text = ""

                next_line_expect_info = True
            elif line.startswith("c"):
                continue
            elif next_line_expect_info and line.startswith('p'):
                next_line_expect_info = False

                current_text += line
            else:
                current_text += line

        current_case.clause_set = write_and_load(current_text)
        cases.append(current_case)

    return cases[1:]

def test_case(case : Case):
    result = execute_sat_solver(case.clause_set, IMPLEMENTATION_TEST_SAT_SOLVER)

    if result is not False:
        if case.is_satisfiable:
            return True, result
        else:
            return False, result
    else:
        if case.is_satisfiable:
            return False, None
        else:
            return True, None

def test_cases(cases) -> list[Case]:
    passed_cases = 0
    total_cases = 0
    failed_cases_count = 0

    failed_cases = []
    
    start = time.time()

    for case in cases:
        successful, assignment = test_case(case)

        if successful:
            passed_cases += 1
        else:
            failed_cases.append(case)

            if assignment is not None:
                print(f"{case.name} Index {failed_cases_count}: Case was unsatisfiable, but got truth assignment {assignment}")
            else:
                print(f"{case.name} Index {failed_cases_count}: Case was satisfiable, but SAT misidentified")

            failed_cases_count += 1

        total_cases += 1

    end = time.time()

    print(f"Passed {passed_cases}/{total_cases}; {passed_cases/total_cases*100:.2f}%")

    elapsed = (end - start) * 1000

    print(f"Elapsed time: {elapsed:.2f}ms")

    return failed_cases

random.seed(GENERATE_SEED)

### MAIN FUNCTIONS
def generate():
    write_cases(
        (generate_case(i) for i in range(GENERATE_NUMBER)),
        GENERATE_FILENAME
    )

def test():
    cases = read_dimacs()

    failed_cases = test_cases(cases)

    write_cases(failed_cases, TEST_RESULT_FILENAME)

def test_on_fly():
    failed_cases = test_cases((
        generate_case(i) for i in range(GENERATE_NUMBER)
    ))

    write_cases(failed_cases, TEST_RESULT_FILENAME)

print("1. Generate cases and write to file\n2. Test from file\n3. Generate and test on the fly")
option = int(input("Enter option: "))

[generate, test, test_on_fly][option - 1]()
