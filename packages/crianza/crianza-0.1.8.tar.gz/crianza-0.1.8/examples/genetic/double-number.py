"""
A genetic programming simulation that produces programs that double their input
values.
"""

import crianza
import crianza.genetic as gp
import random

class DoubleInput(gp.GeneticMachine):
    """A GP machine that produces programs that double their input values.

    E.g., "* 2" or "dup +".
    """
    def __init__(self, code=[]):
        super(DoubleInput, self).__init__(code)
        self._input = 123456

    def new(self, *args, **kw):
        return DoubleInput(*args, **kw)

    def randomize(self, **kw):
        ops = map(crianza.instructions.lookup, ["%", "&", "*", "+", "-", "/",
            "<", "<>", "=", ">", "^", "abs", "and", "bool", "drop", "dup",
            "false", "if", "int", "negate", "not", "or", "over", "rot", "swap",
            "true", "|", "~"])

        return super(DoubleInput, self).randomize(number_string_ratio=1.0,
                instruction_ratio=0.75, restrict_to=ops)

    def setUp(self):
        self._orig = self.code
        self._input = random.randint(0,100)
        self.code = [crianza.compiler.make_embedded_push(self._input)] + self.code

    def tearDown(self):
        self.code = self._orig

    def score(self):
        top = self.top if crianza.isnumber(self.top) else 9999.9

        actual = (top,
                  1000 if self._error else 0,
                  len(self.stack),
                  len(self.return_stack),
                  len(self.code))

        wanted = (self._input*2, # We want to find a way to calculate n*2
                  0, # We don't want errors
                  1, # We the stack to only consist of the answer
                  0, # We want the return stack to be zero
                  2) # We want code to be two instructions

        weights = (0.10, 0.80, 0.02, 0.02, 0.06)
        return 1.0 - gp.weighted_tanimoto(actual, wanted, weights)

    @staticmethod
    def stop(iterations, generation):
        best = sorted(generation, key=lambda m: m.score())
        return gp.average(best, lambda s: s.score()) == 0.0


if __name__ == "__main__":
    print("Starting ...")
    survivors = gp.iterate(DoubleInput, DoubleInput.stop, machines=100)

    print("Listing programs from best to worst, unique solutions only.")
    seen = set()
    maxcount = 15
    for n, m in enumerate(survivors):
        if m.code_string not in seen:
            print("%d %s: %s" % (n, m, m.code_string))
            seen.update([m.code_string])
            maxcount -= 1
            if maxcount < 0:
                break
