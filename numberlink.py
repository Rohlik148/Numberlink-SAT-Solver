import subprocess
from argparse import ArgumentParser

class Process_Input():
    def __init__(self) -> None:
        self.rows = 0
        self.cols = 0
        self.numbers = 0
        self.grid = []
        self.positions = {}
        self.all_cells = []
    
    def load_instance(self, input_file):
        try:
            with open(input_file,'r') as f:
                self.rows = int(f.readline())
                self.cols = int(f.readline())
                self.numbers = int(f.readline())
                for line in f:
                    data = line.strip().split()
                    data = [int(x) for x in data]
                    self.grid.append(data)
            
            for i in range(self.rows):
                for j in range(self.cols):
                    cell_val = self.grid[i][j]
                    if cell_val > 0:  
                        if cell_val not in self.positions:
                            self.positions[cell_val] = [(i, j)]  
                        else:
                            self.positions[cell_val].append((i, j))
                
            self.all_cells = [(i, j) for i in range(self.rows) for j in range(self.cols)]
            
        except Exception as e:
            print("An error occured: ", e)
        
        self._input_validity_check()

        ##########
        #DEBUG:
        #print(f"rows: {self.rows}, columns: {self.cols}, numbers: {self.numbers}")
        #print(self.grid)
        #print(self.positions)
        #print(self.all_cells)
        ##########
    
    def _input_validity_check(self):
        if self.rows < 1 or self.cols < 1 or self.numbers < 1:
            print("Invalid input: first three lines of input must contain a positive integer greater or equal to 1.")
            exit(1)
        
        elif len(self.grid) != self.rows or len(self.grid[0]) != self.cols:
            print("Invalid input: grid does not match parameters given in the irst two lines of an input")
            exit(1) 

class Encoder:
    def __init__(self, ins) -> None:
        self.ins = ins

    def encode(self):
        rows = self.ins.rows
        cols = self.ins.cols
        nums = self.ins.numbers
        positions = self.ins.positions

        vars_count = rows * cols * nums  # Total number of variables
        cnf = []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up

        print("Ensure the start and end cells for each number are set")
        # Ensure the start and end cells for each number are set
        for number, (start, end) in positions.items():
            cnf.append([self._encode_variable(start[0], start[1], number, cols, nums), 0])
            print(cnf[-1])
            cnf.append([self._encode_variable(end[0], end[1], number, cols, nums), 0])
            print(cnf[-1])
        
        print("Ensure at most one number per cell")
        # Ensure at most one number per cell
        for row in range(rows):
            for col in range(cols):
                for n1 in range(1, nums + 1):
                    for n2 in range(n1 + 1, nums + 1):
                        cnf.append([-self._encode_variable(row, col, n1, cols, nums),
                                    -self._encode_variable(row, col, n2, cols, nums), 0])
                        print(cnf[-1])

        print("Ensure exactly one value per cell")
        # Ensure exactly one value per cell
        for i in range(rows):
            for j in range(cols):
                clause = [self._encode_variable(i, j, k, cols, nums) for k in range(1, nums + 1)]
                clause.append(0)
                cnf.append(clause)
                print(cnf[-1])

        # Ensure path connectivity with the constraint on start, end
        print("Ensure each start/end cell has exactly one neighbor")
        endpoints = []
        for number, (start, end) in positions.items():
            for endpoint in [start, end]:
                endpoints.append(endpoint)
                i, j = endpoint  # Coordinates of the endpoint
                neighbors = [
                    (i + di, j + dj)
                    for di, dj in directions
                    if 0 <= i + di < rows and 0 <= j + dj < cols
                ]
                clause = [-self._encode_variable(i, j, number, cols, nums)]
                for ni, nj in neighbors:
                    clause.append(self._encode_variable(ni, nj, number, cols, nums))
                cnf.append(clause + [0])  # End clause
                print(cnf[-1])
                clause.pop(0)
                for k in range(len(clause)):
                    for l in range(k+1,len(clause)):
                        cnf.append([-clause[k],-clause[l],0])
                        print(cnf[-1])
        
        # Ensure path connectivity for non-endpoint cells
        print("Ensure path connectivity for non-endpoint cells")
        for i in range(rows):
            for j in range(cols):
                if (i, j) not in endpoints:
                    neighbors = [
                        (i + di, j + dj)
                        for di, dj in directions
                        if 0 <= i + di < rows and 0 <= j + dj < cols
                    ]
                    for number, (start, end) in positions.items():
                        clause = [-self._encode_variable(i, j, number, cols, nums)]
                        for ni, nj in neighbors:
                            clause.append(self._encode_variable(ni, nj, number, cols, nums))
                        cnf.append(clause + [0])
                        print(cnf[-1])
                        clause.pop(0)
                        if len(clause) > 2:
                            for k in range(len(clause)):
                                for l in range(k+1,len(clause)):
                                    for m in range(l+1,len(clause)):
                                        cnf.append([-clause[k],-clause[l],-clause[m],0])
                                        print(cnf[-1])

        return cnf, vars_count

    def _encode_variable(self, i, j, k, cols, nums):
        return (i * cols * nums) + (j * nums) + k


class SAT_Solver:
    def __init__(self, solver, verbosity) -> None:
        self.solver = solver
        self.verb = verbosity

    def call_solver(self, cnf, vars_count, output_file_name):
        # Print CNF into formula.cnf in DIMACS format
        with open(output_file_name, "w") as file:
            file.write("p cnf " + str(vars_count) + " " + str(len(cnf)) + '\n')
            for clause in cnf:
                file.write(' '.join(str(literal) for literal in clause) + '\n')

        # Call the solver and return the output
        return subprocess.run(['./' + self.solver, '-model', '-verb=' + str(self.verb), output_file_name], stdout=subprocess.PIPE)

    def print_result(self, result, ins):
        '''for line in result.stdout.decode('utf-8').split('\n'):
            print(line) '''                    # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself

        # check the returned result
        if (result.returncode == 20):       # returncode for SAT is 10, for UNSAT is 20
            return

        print()
        print("##################################################################")
        print("###########[ Human readable result of the tile puzzle ]###########")
        print("##################################################################")
        print()

        
        # Parse the output from the SAT solver
        model = []
        for line in result.stdout.decode('utf-8').split('\n'):
            if line.startswith("v"):
                vars = line.split(" ")
                vars.remove("v")
                model.extend(int(v) for v in vars)
        model = [v for v in model if v > 0]  # Filter positive literals
        
        print("model:", model)

        # Decode the model into the grid
        grid = [[0 for _ in range(ins.cols)] for _ in range(ins.rows)]
        for var in model:
            var -= 1
            k = var % ins.numbers + 1
            j = (var // ins.numbers) % ins.cols
            i = var // (ins.numbers * ins.cols)
            grid[i][j] = k

        # Print the grid
        print("\nThe complete grid is:")
        for row in grid:
            print(" ".join(map(str, row)))

class Numberlink():
    if __name__ == "__main__":
        
        parser = ArgumentParser()

        parser.add_argument(
            "-i",
            "--input",
            default="input.in",
            type=str,
            help=(
                "The instance file."
            ),
        )
        parser.add_argument(
            "-o",
            "--output",
            default="formula.cnf",
            type=str,
            help=(
                "Output file for the DIMACS format (i.e. the CNF formula)."
            ),
        )
        parser.add_argument(
            "-s",
            "--solver",
            default="glucose-syrup",
            type=str,
            help=(
                "The SAT solver to be used."
            ),
        )
        parser.add_argument(
            "-v",
            "--verb",
            default=1,
            type=int,
            choices=range(0,2),
            help=(
                "Verbosity of the SAT solver used."
            ),
        )
        args = parser.parse_args()

        # get the input instance
        input_processor = Process_Input()
        input_processor.load_instance(args.input)

        # encode the problem to create CNF formula
        encoder = Encoder(input_processor)
        cnf, vars_count = encoder.encode()

        # call the SAT solver and get the result
        solver = SAT_Solver(args.solver, args.verb)
        result = solver.call_solver(cnf, vars_count, args.output)

        # interpret the result and print it in a human-readable format
        solver.print_result(result,input_processor)