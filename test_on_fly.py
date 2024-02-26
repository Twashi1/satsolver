import generator
# TODO: rely on this more for general testing code
import tester

def generate_and_test(configs, working_sat, test_sat, is_simple_sat_solve_work=True, is_simple_sat_solve_test=False):
    passed_cases = 0
    failed_cases = []
    
    for i, config in enumerate(configs):
        clause_set = generator.generate_clause_set(config)

        satisfiability = None

        if is_simple_sat_solve_work: satisfiability = working_sat(clause_set) is not False
        else: satisfiability = working_sat(clause_set, []) is not False

        result = None

        if is_simple_sat_solve_test: result = test_sat(clause_set)
        else: result = test_sat(clause_set, [])

        if result is False:
            if not satisfiability:
                passed_cases += 1
            else:
                print(f"Test index {i} failed, expected satisfiable")
                failed_cases.append((clause_set, satisfiability))
        else:
            if satisfiability:
                passed_cases += 1
            else:
                print(f"Test index {i} failed, {result} is not a satisfying truth assignment")
                failed_cases.append((clause_set, satisfiability))
        
        if tester.REQUIRE_ALL_VARIABLES and result is not False and satisfiability:
            variables = {abs(literal) for clause in clause_set for literal in clause}

            if variables != {abs(literal) for literal in result}:
                print(f"Warning index {i} assignment {result} did match expected variables: {variables}")

    print(f"Passed {passed_cases}/{len(configs)}, {passed_cases/len(configs)*100:.3f}%")
    if len(failed_cases) > 0: print(f"Writing failed cases to text file")

    with open("results.txt", "w+") as f:
        for i, case in enumerate(failed_cases):
            word = 'satisfiable' if case[1] else 'unsatisfiable'

            f.write(f"# {i} {word}\n{generator.dimacs_string(case[0])}\n")

# import your own [WORKING] implementation here (and remove these three lines)
import sys
sys.path.append("secret/")
import implementation

# Generate test cases with a working implementation, and then run them on a different implementation
# Writes failed cases to a text file

generate_and_test(
    generator.generate_configs(1000, (3, 3), (4, 4)),    # n cases, with a-b variables and c-d clauses
    implementation.simple_sat_solve,                    # your known working sat-solve function
    implementation.dpll_sat_solve,                      # sat solve to test
    True,                                               # using simple sat solve as tester, so true
    False                                               # testing dpll sat solve, so false
)