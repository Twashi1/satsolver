# Configure and run at bottom of file
# Some global variables to edit

# Require all variables' value to be stated, not just a partial assignment
# e.g. [[-1, 3], [1, 2]] requires [2, 3, (+-)1] not just [2, 3]
REQUIRE_ALL_VARIABLES = True

def read_extended_dimacs(file):
    with open(file, 'r') as f:
        lines = f.readlines()

        tests = []
        headers = [i for i, line in enumerate(lines) if line.startswith("#")]

        i = 0

        for i, header in enumerate(headers):
            line = lines[header]
            next_header = None if i + 1 >= len(headers) else headers[i + 1]

            _, name, satisfiability = line.split(" ")
            tests.append((name, satisfiability[:-1] in ('satisfiable', 'sat'), lines[header + 1:next_header]))

        return tests
    
def write_test(test, filename):
    with open(filename, 'wt+') as f:
        for line in test[2]:
            if len(line) <= 1 or line.startswith("c"):
                continue

            f.write(line)
    
def test_solve(test, sat_solve, dimacs_loader, is_simple_sat_solver):
    # trash
    write_test(test, "temp.txt")

    result = None

    if is_simple_sat_solver:
        result = sat_solve(dimacs_loader("temp.txt"))
    else:
        result = sat_solve(dimacs_loader("temp.txt"), [])

    if result is False:
        if not test[1]:
            return True

        print(f"{test[0]} failed, expected satisfiable")

        return False
    
    if not test[1]:
        print(f"{test[0]} failed, {result} is not a satisfying truth assignment")

        return False
    
    if REQUIRE_ALL_VARIABLES:
        # super trash
        clause_set = dimacs_loader("temp.txt")
        vars = set()

        for clause in clause_set:
            for var in clause: vars.add(abs(var))

        if len(vars) != len(result):
            print(f"Warning: assignment {result} did not contain all literals: {vars}")

    return True

# Test extended dimacs format
def test_extended(filename, sat_solve, dimacs_loader, is_simple_sat_solver):
    tests = read_extended_dimacs(filename)

    passed = 0

    for test in tests:
        result = test_solve(test, sat_solve, dimacs_loader, is_simple_sat_solver)
        if result: passed += 1

    print(f"Finished {len(tests)}")
    print(f"{passed}/{len(tests)}, {(passed/len(tests)) * 100:.3f}%")

# Configure and run here

# ignore this (importing my own solution from folder)
import sys
sys.path.append("secret/")
import implementation

# name of the test file to read, expecting "extended" dimacs format
# basically each test is separated by # testName [un]satisfiable e.g. "tests/simple.txt"
testName = "tests/1k4v16c.txt"
# function to load dimacs file, expecting just to take a filename
dimacs_loader = implementation.load_dimacs
# function to SAT-solve, expecting to take a clause set and a partial assignment
sat_solver = implementation.simple_sat_solve
# if you're testing your simple sat solver, set this to true so a partial assignment is not required
is_simple_sat_solver = True

if sat_solver is not None:
    test_extended(testName, sat_solver, dimacs_loader, is_simple_sat_solver)
else:
    print("Configure in file (import it, and set value of the sat_solver variable)")