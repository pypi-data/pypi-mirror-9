#!/usr/bin/env python
"""
This probably would give us a much better chance of avoiding collisions,
but it also increases the memory requirements by quite a bit--additionally,
31 handles things quite well for more than 33 million combinations
"""
import gmpy as _gmpy


class new():
    """ incMulHash is the primary class for generating hashes """
    runningHash = None
    # P = 11400714819323198485
    # The following is likely our best candidate, it is a 32 bit fib-prime
    _P = 2971215073
    _gP = _gmpy.mpz(_P)
    # P = 31
    """
        This is for allowing users to define
        which hashes they would like included
    """
    # includedHashes = {xor: lambda newData: 1 + newData}

    def add(self, newData):
        if self.runningHash is None:
            x = 1 + newData
            s = self._P + 2 * newData
            m = (self._gP + 2 * newData)/2
        else:
            x, s, m = self.runningHash
            x ^= 1 + newData
            s += self._P + 2 * newData
            m = ((self._gP + 2 * newData) * ((2 * m) + 1))/2
            """ I believe m,x,s is faster for comparison than x,s,m """
        self.runningHash = (x, s, m)
        return self.runningHash

    def remove(self, data):
        try:
            x, s, m = self.runningHash
            x ^= 1 + data
            s -= self._P + 2 * data
            m = (((2 * m) + 1) / (self._gP + 2 * data)) / 2
            self.runningHash = (x, s, m) if (x, s, m) != (0, 0, 0) else None
        except:
            pass
        return self.runningHash

__all__ = (new)

"""
This is for testing purposes and is run when this file is run directly.
If run directly, you can pass in an argument dictating the number of
unique possible values. 25 is maybe too big for most systems.
"""
if __name__ == "__main__":
    import sys
    import timeit
    import itertools
    from random import randrange

    def test():
        fac = _gmpy.fac
        com = _gmpy.comb
        end = 7
        isRandom = False
        try:
            end = int(sys.argv[1])
            isRandom = True if sys.argv[3] == "true" else False
        except:
            pass

        shiftsRange = range(1, end+1)
        possibleShifts = len(shiftsRange)
        # The number 2016 is just the number of 5 minute increments in a week.
        # 100 is used to represent the number of employees.
        realPossibleShifts = _gmpy.comb(2016, 2)*100
        if isRandom:
            shifts = [randrange(0, realPossibleShifts) for _ in xrange(end)]
        else:
            shifts = shiftsRange[:]
        # xmuHashes = set()
        xsmHashes = set()
        facPossible = fac(possibleShifts)
        comb = reduce(lambda total, numOfShiftsChosen:
                      total+com(possibleShifts, numOfShiftsChosen),
                      shiftsRange, 0)
        perm = reduce(lambda total, numOfShiftsChosen:
                      total+(facPossible/(fac(possibleShifts-numOfShiftsChosen))),
                      shiftsRange, 0)
        print("Combinations :", comb)
        print("Permutations :", perm)
        for n in shiftsRange:
            print(n)
            for schedule in itertools.combinations(shifts, n):
                hasher = new()
                for shift in schedule:
                    hasher.add(shift)
                x, s, m = hasher.runningHash
                # xmuHashes.add((x, s,))
                xsmHashes.add((x, s, m,))

        # print("xmuHashesSet :", len(xmuHashes))
        print("xsmHashesSet :", len(xsmHashes))
        print("Combinations :", comb)
        print("Permutations :", perm)
        print("Comb/Perm %  :", 100*(float(comb)/float(perm)))
        try:
            print("Three Hashes :",
                  # xmuHashes.pop(),
                  # xmuHashes.pop(),
                  # xmuHashes.pop())
                  xsmHashes.pop(),
                  xsmHashes.pop(),
                  xsmHashes.pop())
        except:
            pass

    numOfRuns = 10000
    numOfReps = 3
    try:
        numOfRuns = int(sys.argv[2])
        numOfReps = int(sys.argv[4])
    except:
        pass
    print(timeit.repeat("test()",
                        repeat=numOfReps,
                        setup="from __main__ import test",
                        number=numOfRuns))
    sys.exit()
