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
        self.dic = {}
        self.dicnum = 1

    def encode(self):
        rows = self.ins.rows
        cols = self.ins.cols
        nums = self.ins.numbers
        positions = self.ins.positions
        
        vars_count = rows * cols * nums  # Total number of variables
        cnf = []
        
        for i in range(rows):
            for j in range(cols):
                for k in range(1,nums+1):
                    self.dic[(i,j,k)] = self.dicnum
                    self.dicnum += 1
        
        # Ensure the start and end cells for each number are set
        for number, (start, end) in positions.items():
            cnf.append([self._encode_variable(start[0], start[1], number), 0])
            cnf.append([self._encode_variable(end[0], end[1], number), 0])
        
        # Ensure exactly one value per cell
        for i in range(rows):
            for j in range(cols):
                clause = [self._encode_variable(i, j, k) for k in range(1, nums + 1)]
                clause.append(0)
                cnf.append(clause)
                clause = [-self._encode_variable(i, j, k) for k in range(1, nums + 1)]
                clause.append(0)
                cnf.append(clause)
        
        # Add "at most one value per cell" constraints
        for i in range(rows):
            for j in range(cols):
                for k in range(1, nums + 1):
                    for l in range(k + 1, nums + 1):
                        cnf.append([-self._encode_variable(i, j, k), -self._encode_variable(i, j, l), 0])
        
        endpoints = []
        for number, (start,end) in positions.items():
            endpoints.append(start)
            endpoints.append(end)
        
        for number in range(1,nums+1):
            for i in range(rows):
                for j in range(cols):
                    neighbors = self.get_neighbors(i, j, rows, cols)
                    # For endpoint
                    if (i, j) in endpoints and (i,j) in positions[number]:
                        clause = []
                        for ni, nj in neighbors:
                            clause.append(self._encode_variable(ni, nj, number))
                        clause.append(0)
                        cnf.append(list(clause))
                        clause.pop(-1)
                        for k in range(len(clause)):
                            for l in range(k+1,len(clause)):
                                cnf.append([-clause[k], -clause[l], 0])
                    # for non-endpoint    
                    elif (i, j) not in endpoints:
                        clause = []
                        for ni, nj in neighbors:
                            clause.append(self._encode_variable(ni, nj, number))
                        var = -self._encode_variable(i,j,number)
                        for k in range(len(clause)):
                            for l in range(k+1,len(clause)):
                                cnf.append([var,clause[k],clause[l],0])
                        if len(clause) > 2:
                            for m in range(len(clause)):
                                for n in range(m+1,len(clause)):
                                    for o in range(n+1,len(clause)):
                                        cnf.append([var,-clause[m],-clause[n],-clause[o],0])
        
        return cnf, vars_count, self.dic

    def _encode_variable(self, i, j, k):
            return self.dic[(i,j,k)]

    def get_neighbors(self, i, j, rows, cols):
        neighbors = []
        if i > 0: neighbors.append((i - 1, j))  # Up
        if i < rows - 1: neighbors.append((i + 1, j))  # Down
        if j > 0: neighbors.append((i, j - 1))  # Left
        if j < cols - 1: neighbors.append((i, j + 1))  # Right
        return neighbors

class SAT_Solver:
    def __init__(self, solver, verbosity) -> None:
        self.solver = solver
        self.verb = verbosity

    def call_solver(self, cnf, vars_count, output_file_name):
        # print CNF into formula.cnf in DIMACS format
        with open(output_file_name, "w") as file:
            file.write("p cnf " + str(vars_count) + " " + str(len(cnf)) + '\n')
            for clause in cnf:
                file.write(' '.join(str(lit) for lit in clause) + '\n')


        # Call the solver and return the output
        return subprocess.run(['./' + self.solver, '-model', '-verb=' + str(self.verb), output_file_name], stdout=subprocess.PIPE)

    def print_result(self, result, ins, dict):
        '''for line in result.stdout.decode('utf-8').split('\n'):
            print(line) '''                    # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself

        # check the returned result
        if (result.returncode == 20): # returncode for SAT is 10, for UNSAT is 20
            print("Unsolvable")
            return

        print()
        print("##################################################################")
        print("###########[ Human readable result of the tile puzzle ]###########")
        print("##################################################################")
        print()

        
        model = []
        for line in result.stdout.decode('utf-8').split('\n'):
            if line.startswith("v"):    # there might be more lines of the model, each starting with 'v'
                vars = line.split(" ")
                vars.remove("v")
                model.extend(int(v) for v in vars)      
        model.remove(0) # 0 is the end of the model, just ignore it
        
        grid = [[0 for i in range(ins.cols)] for j in range(ins.rows)]
        for var in model:
            if var > 0:
                for key, value in dict.items():
                    if value == var:
                        grid[key[0]][key[1]] = key[2]
                        
        for row in grid:
            print(*row)

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
        cnf, vars_count, enc_dict = encoder.encode()

        # call the SAT solver and get the result
        solver = SAT_Solver(args.solver, args.verb)
        result = solver.call_solver(cnf, vars_count, args.output)

        # interpret the result and print it in a human-readable format
        solver.print_result(result,input_processor, enc_dict)