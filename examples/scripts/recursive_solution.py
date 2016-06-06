class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        if workers is None:
            workers = []
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        print("Job Started")
        print("Workers count: %d." % len(self.workers))

        count = self.workers[0].recursion(1, len(self.workers)).value

        self.write_output(count)

        print("Count = ", count)
        print("Job Finished")

    def recursion(self, depth, max_depth):
        if depth < max_depth:
            return 1 + self.workers[depth].recursion(depth + 1, max_depth).value
        else:
            return 1

    def write_output(self, output):
        f = open(self.output_file_name, 'w')
        f.write(str(output))
        f.write('\n')
        f.close()
        print("output done")
