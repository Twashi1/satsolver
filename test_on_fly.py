import generator

def generate_and_test(configs, working_sat, test_sat, literal_presence_weight=generator.DEFAULT_LITERAL_PRESENCE_WEIGHT, require_all_literals=True, is_simple_sat_solve_work=True, is_simple_sat_solve_test=False):
    passed_cases = 0
    failed_cases = []
    
    for i, config in enumerate(configs):
        clause_set = generator.generateClauseSet(config, literal_presence_weight)

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
        
        if require_all_literals and result is not False and satisfiability:
            vars = set()

            for clause in clause_set:
                for var in clause: vars.add(abs(var))

            if len(vars) != len(result):
                print(f"Warning index {i} assignment {result} did not contain all literals: {vars}")

    print(f"Passed {passed_cases}/{len(configs)}, {passed_cases/len(configs)*100:.3f}%")
    if len(failed_cases) > 0: print(f"Writing failed cases to text file")

    for i, case in enumerate(failed_cases):
        with open("results.txt", "r") as f:
            word = 'satisfiable' if case[1] else 'unsatisfiable'

            f.write(f"# {i} {word}\n{generator.dimacs(case[0])}\n")

# import your own [WORKING] implementation here (and remove these three lines)
import sys
sys.path.append("secret/")
import implementation

# Generate test cases with a working implementation, and then run them on a different implementation
# Writes failed cases to a text file

generate_and_test(
    generator.generateConfigs(1000, (3, 3), (4, 4)),    # n cases, with a-b variables and c-d clauses
    implementation.simple_sat_solve,                    # your known working sat-solve function
    implementation.dpll_sat_solve,                      # sat solve to test
    generator.DEFAULT_LITERAL_PRESENCE_WEIGHT,
    True,                                               # require all literals
    True,                                               # using simple sat solve as tester, so true
    False                                               # testing dpll sat solve, so false
)