import re
from Pyro4.futures import FutureResult


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        if workers is None:
            workers = []
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        self.function = None
        self.memory = {}

    def set_function(self, function):
        self.function = function

    @staticmethod
    def get_value(future_or_value):
        if isinstance(future_or_value, FutureResult):
            return future_or_value.value
        else:
            return future_or_value

    @staticmethod
    def list_to_string(l):
        return ":".join(map(lambda x: str(x), l))

    def solve(self):
        print("Job Content Addressable Memory started")
        print("Workers count: %d." % len(self.workers))

        function, arguments_list = self.read_input()
        print("     Arguments:")
        print("Function: " + function)
        print("Arguments count: " + str(len(arguments_list)))

        for worker in self.workers:
            worker.set_function(function)

        chunk_size = len(arguments_list) / len(self.workers) + 1
        chunks = [arguments_list[i:i + chunk_size] for i in xrange(0, len(arguments_list), chunk_size)]

        chunks_results = []

        for index, chunk in enumerate(chunks):
            chunks_results.append(self.workers[index].evaluate_function(chunk))

        results = []

        for result in chunks_results:
            results = results + Solver.get_value(result)

        self.write_output(results)

        print("Job Finished")

    def find_value(self, arguments):
        key = Solver.list_to_string(arguments)
        return self.memory.get(key)

    def put_value(self, arguments, value):
        key = Solver.list_to_string(arguments)
        self.memory[key] = value

    def evaluate_function(self, arguments_list):
        results = []
        for arguments in arguments_list:
            value = self.find_value(arguments)
            if not value:
                for worker in self.workers:
                    if not worker.is_self:
                        value = Solver.get_value(worker.find_value(arguments))
                        if value:
                            break
            if not value:
                arg_indexes = re.findall('x([0-9]+)', self.function)
                func_expr = self.function
                for arg_index in arg_indexes:
                    func_expr = func_expr.replace('x' + arg_index, str(arguments[int(arg_index) - 1]))
                value = eval(func_expr)
            results.append(value)
            self.put_value(arguments, value)
        return results

    def read_input(self):
        f = open(self.input_file_name, 'r')

        function = f.readline()

        arguments_count = int(f.readline())
        arguments = []
        for i in xrange(0, arguments_count):
            arguments.append(f.readline().split(' '))

        f.close()
        return function, arguments

    def write_output(self, results):
        f = open(self.output_file_name, 'w')

        for result in results:
            f.write(str(result))
            f.write('\n')

        f.close()

# s = Solver([Solver(), Solver()],
#            '/path/to/input/file',
#            '/path/to/output/file')
# s.solve()
