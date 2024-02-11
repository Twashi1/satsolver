# GO BOTTOM

# TODO: tester for unit propogation

def readExtendedDIMACS(file):
    with open(file, 'r') as f:
        lines = f.readlines()

        tests = []
        headers = [i for i, line in enumerate(lines) if line.startswith("#")]

        i = 0

        for i, header in enumerate(headers):
            line = lines[header]
            nextHeader = None if i + 1 >= len(headers) else headers[i + 1]

            _, name, satisfiability = line.split(" ")
            tests.append((name, satisfiability[:-1] in ('satisfiable', 'good'), lines[header + 1:nextHeader]))

        return tests
    
def writeTest(test, filename):
    with open(filename, 'wt+') as f:
        for line in test[2]:
            if len(line) <= 1:
                continue

            f.write(line)
    
def testSolve(test, sat_solve, dimacs_loader, is_simple_sat_solver):
    writeTest(test, "temp.txt")

    result = None

    if is_simple_sat_solver:
        result = sat_solve(dimacs_loader("temp.txt"))
    else:
        result = sat_solve(dimacs_loader("temp.txt"), [])

    if result is False:
        if not test[1]:
            print(f"{test[0]} passed")

            return True

        print(f"{test[0]} failed, expected satisfiable")

        return False
    
    if not test[1]:
        print(f"{test[0]} failed, {result} is not a satisfying truth assignment")

        return False
    
    print(f"{test[0]} passed")

    return True

# test extended dimacs format
def testExtended(filename, sat_solve, dimacs_loader, is_simple_sat_solver):
    tests = readExtendedDIMACS(filename)

    passed = 0

    for test in tests:
        result = testSolve(test, sat_solve, dimacs_loader, is_simple_sat_solver)
        if result: passed += 1

    print(f"Finished {len(tests)}")
    print(f"{passed}/{len(tests)}, {(passed/len(tests)) * 100:.3f}%")

### FILL IN DETAILS HERE

# ignore this    
import sys
sys.path.append("secret/")
import implementation

# name of the test file to read, expecting "extended" dimacs format
# basically each test is separated by # testName [un]satisfiable e.g. "tests/simple.txt"
testName = "tests/simple.txt"
# function to load dimacs file, expecting just to take a filename
dimacs_loader = implementation.load_dimacs
# function to SAT-solve, expecting to take a clause set and a partial assignment
sat_solver = implementation.simple_sat_solve
# if you're testing your simple sat solver, set this to true so a partial assignment is not required
is_simple_sat_solver = True

if sat_solver is not None:
    testExtended(testName, sat_solver, dimacs_loader, is_simple_sat_solver)
else:
    print("Configure in file (import it, and set value of the sat_solver variable)")