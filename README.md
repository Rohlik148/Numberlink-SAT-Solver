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

The **numberlink** is a logic-based pathfinding game played on a grid. Each puzzle consists of a grid where numbered pairs (start and end points) are given. The objective is to connect each pair with a continuous path, such that:

1) Paths do not cross or overlap.

2) Every cell on the grid is either part of a path or remains empty.

The challenge lies in finding a solution that satisfies these constraints while covering all required connections. More information [here](https://en.wikipedia.org/wiki/Numberlink).

An example of a valid input format is:

```
3
3
2
1 2 0
0 1 0
2 0 0
```

where the first line is the number of rows of the grid, the second line is the number of columns of the grid, and the third line is the number of pairs of numbers to be connected.

The target position has all cells filled with numbers and satisfies the constraints stated above.

```
1 2 2
1 1 2
2 2 2
```

## Encoding

Will be added later.

## User documentation

Basic usage: 
```
numberlink.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]
```

Command-line options:

* `-h`, `--help` : Show a help message and exit.
* `-i INPUT`, `--input INPUT` : The instance file. Default: "input.in".
* `-o OUTPUT`, `--output OUTPUT` : Output file for the DIMACS format (i.e. the CNF formula).
* `-s SOLVER`, `--solver SOLVER` : The SAT solver to be used.
*  `-v {0,1}`, `--verb {0,1}` :  Verbosity of the SAT solver used.

## Example instances

* `input.in`: A solvable basic 3x3 instance.
* `input-easy.in`: A solvable easy 5x5 instance.
* `input-medium.in`: A solvable medium 11x11 instance.

More will be added later.

## Experiments

Will be added later.
