# Numberlink-SAT-Solver

The provided Python code encodes, solves, and decodes the **numberlink** puzzle via reduction to SAT (i.e. propositional logic formula).

The SAT solver used is [Glucose](https://www.labri.fr/perso/lsimon/research/glucose/), more specifically [Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1). The source code is compiled using

```
cmake .
make
```

This example contains a compiled UNIX binary of the Glucose solver. For optimal experience, we encourage the user to compile the SAT solver themselves. Note that the solver, as well as the Python script, are assumed to work on UNIX-based systems. In case you prefer using Windows, we recommend to use WSL.

Note that the provided encoding for the sliding tile puzzle is not the only existing encoding. Usually, there are several equivalent encodings one might use. Choosing the encoding is up to the user based on experience and experiments.

Also note, that the puzzle is an optimization problem (i.e. try to solve it in as few steps as possible), however, SAT is a decision problem, therefore, we transfer the puzzle into a decision problem for a specific number of moves (i.e. is there a solution with this many moves?). To find the minimum number of moves, one has to solve a sequence of decision problems with a different number of moves allowed.

The following documentation is an acceptable solution format that should accompany your code.

# Documentation

## Problem description
