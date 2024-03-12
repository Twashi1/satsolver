# satsolver

Testing a SAT-solver, and generating test cases for a SAT-solver

## Usage

`tester.py` - Fill out the options in the file, then run and select option to run

## DIMACS

Packs multiple DIMACS-formatted tests into one file using the following format:
```
p cnf <variable max> <clause count>
c special <sat|unsat> <test name>
1 2 3 0
1 2
-3 0
<clause area>
```

Clauses must be terminated with a `0`, and can stretch over multiple lines (although the generator never generates them like this)

## Generator

### Options
- `LITERAL_PRESENCE_WEIGHT` - The chance any given literal has to be present in a clause
- `CLAUSE_GENERATION_ATTEMPT_LIMIT` - The attempts to generate a clause before we give up so we don't get stuck in an infinite loop trying to generate an impossible clause
- `NO_MISSING_VARIABLES` - Ensure we generate all variables from $[1,n]$ in the clause set, so there's no gaps
- `ALLOW_EMPTY_CLAUSES` - Allow empty clauses to generate in the clause set

### Variables
- `GENERATE_FILENAME` cba to write them out
- blah
- blah

### Inaccuracies/Subtleties

- Can generate duplicate clauses
- (Optional) Can generate duplicate literals in the same clause (and of opposite polarity)
- (Optional) Can generate empty clauses
- (Optional) Can generate with missing variables in range $[1, n]$ where $n$ is maximum variable