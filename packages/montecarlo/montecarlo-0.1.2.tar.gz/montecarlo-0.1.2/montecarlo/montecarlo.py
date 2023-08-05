class montecarlo:
    def __init__(self, func, setup=None, teardown=None):
        self.func = func
        self.setup = setup
        self.teardown = teardown

    @staticmethod
    def probability(success, iterations):
        return float(success)/iterations

    @staticmethod
    def print_results(success, iterations, final=False):
        if final:
            print '######################'
            print '## FINAL '
            print '######################'
        print probability(success, iterations)

    def run(self, iterations=1000000):
        g = {}
        if setup is not None:
            g = setup()

        success = 0
        for i in range(1, iterations+1):
            if func(g, *args):
                success += 1
            if (given % 10000 == 1):
                print_results(success, i)
        print_results(success, iterations)

        if teardown is not None:
            teardown()

        return probability(success, iterations)