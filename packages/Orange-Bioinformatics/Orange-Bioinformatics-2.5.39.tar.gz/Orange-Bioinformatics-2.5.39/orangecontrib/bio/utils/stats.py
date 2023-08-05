import math
import threading
import six


def _lngamma(z):
    x = 0
    x += 0.1659470187408462e-06 / (z + 7)
    x += 0.9934937113930748e-05 / (z + 6)
    x -= 0.1385710331296526 / (z + 5)
    x += 12.50734324009056 / (z + 4)
    x -= 176.6150291498386 / (z + 3)
    x += 771.3234287757674 / (z + 2)
    x -= 1259.139216722289 / (z + 1)
    x += 676.5203681218835 / (z)
    x += 0.9999999999995183
    
    return math.log(x) - 5.58106146679532777 - z + (z - 0.5) * math.log(z + 6.5)
        

class LogBin(object):
    _max = 2
    _lookup = [0.0, 0.0]
    _max_factorial = 1
    _lock = threading.Lock()

    def __init__(self, max=1000):
        self._extend(max)

    @staticmethod
    def _extend(max):
        with LogBin._lock:
            if max <= LogBin._max:
                return
            for i in range(LogBin._max, max):
                if i > 1000: ## an arbitrary cuttof
                    LogBin._lookup.append(LogBin._logfactorial(i))
                else:
                    LogBin._max_factorial *= i
                    LogBin._lookup.append(math.log(LogBin._max_factorial))
            LogBin._max = max

    def _logbin(self, n, k):
        if n >= self._max:
            self._extend(n + 100)
        if k < n and k >= 0:
            return self._lookup[n] - self._lookup[n - k] - self._lookup[k]
        else:
            return 0.0

    @staticmethod
    def _logfactorial(n):
        if (n <= 1):
            return 0.0
        else:
            return _lngamma(n + 1)

class Binomial(LogBin):
    """ `Binomial distribution 
    <http://en.wikipedia.org/wiki/Binomial_distribution>`_ is a discrete
    probability distribution of the number of successes in a sequence
    of n independent yes/no experiments, each of which yields success
    with probability p. """

    def __call__(self, k, N, m, n):
        """ If m out of N experiments are positive return the probability
        that k out of n experiments are positive using the binomial
        distribution: if p = m/N then return bin(n,k)*(p**k + (1-p)**(n-k))
        where bin is the binomial coefficient. """

        p = 1.0 * m / N
        if p == 0.0:
            if k == 0:
                return 1.0
            else:
                return 0.0
        elif p == 1.0:
            if n == k:
                return 1.0
            else:
                return 0.0
        try:
            return min(math.exp(self._logbin(n, k) + k * math.log(p) + (n - k) * math.log(1.0 - p)), 1.0)
        except (OverflowError, ValueError) as er:
            print(k, N, m, n)
            raise
##        return math.exp(self._logbin(n, k) + math.log((p**k) * (1.0 - p)**(n - k)))

    def p_value(self, k, N, m, n):
        """ The probability that k or more tests are positive. """
        if n - k + 1 <= k:
            #starting from k gives the shorter list of values
            return sum(self.__call__(i, N, m, n) for i in range(k, n+1))
        else:
            value = 1.0 - sum(self.__call__(i, N, m, n) for i in range(k))
            #if the value is small it is probably inexact due to the limited
            #precision of floats, as for example  (1-(1-1e-20)) -> 0
            #if so, compute the result without substraction
            if value < 1e-3: #arbitary threshold
                #print "INEXACT", value, sum(self.__call__(i, N, m, n) for i in range(k, n+1))
                return sum(self.__call__(i, N, m, n) for i in range(k, n+1))
            else:
                return value

class Hypergeometric(LogBin):
    """ `Hypergeometric distribution
    <http://en.wikipedia.org/wiki/Hypergeometric_distribution>`_ is
    a discrete probability distribution that describes the number of
    successes in a sequence of n draws from a finite population without
    replacement. 

    """

    def __call__(self, k, N, m, n):
        """If m out of N experiments are positive return the probability
        that k out of n experiments are positive using the hypergeometric
        distribution (i.e. return bin(m, k)*bin(N-m, n-k)/bin(N,n)
        where bin is the binomial coefficient).
        """
        if k < max(0, n + m - N) or k > min(n, m):
            return 0.0
        try:
            return min(math.exp(self._logbin(m, k) + self._logbin(N - m, n - k) - self._logbin(N, n)), 1.0)
        except (OverflowError, ValueError) as er:
            print(k, N, m, n)
            raise

    def p_value(self, k, N, m, n):
        """ 
        The probability that k or more tests are positive.
        """

        if min(n,m) - k + 1 <= k:
            #starting from k gives the shorter list of values
            return sum(self.__call__(i, N, m, n) for i in range(k, min(n,m)+1))
        else:
            value = 1.0 - sum(self.__call__(i, N, m, n) for i in (range(k)))
            #if the value is small it is probably inexact due to the limited
            #precision of floats, as for example  (1-(1-1e-20)) -> 0
            #if so, compute the result without substraction
            if value < 1e-3: #arbitary threshold
                #print "INEXACT", value, sum(self.__call__(i, N, m, n) for i in range(k, min(n,m)+1))
                return sum(self.__call__(i, N, m, n) for i in range(k, min(n,m)+1))
            else:
                return value

## to speed-up FDR, calculate ahead sum([1/i for i in range(1, m+1)]), for m in [1,100000]. For higher values of m use an approximation, with error less or equal to 4.99999157277e-006. (sum([1/i for i in range(1, m+1)])  ~ log(m) + 0.5772..., 0.5572 is an Euler-Mascheroni constant) 
c = [1.0]
for m in range(2, 100000):
    c.append( c[-1] + 1.0/m)

def is_sorted(l):
    return all(l[i] <= l[i+1] for i in range(len(l)-1))

def FDR(p_values, dependent=False, m=None, ordered=False):
    """
    `False Discovery Rate <http://en.wikipedia.org/wiki/False_discovery_rate>`_ correction on a list of p-values.

    :param p_values: a list of p-values.
    :param dependent: use correction for dependent hypotheses (default False).
    :param m: number of hypotheses tested (default ``len(p_values)``).
    :param ordered: prevent sorting of p-values if they are already sorted (default False).
    """

    if not ordered:
        ordered = is_sorted(p_values)

    if not ordered:
        joined = [ (v,i) for i,v in enumerate(p_values) ]
        joined.sort()
        p_values = [ p[0] for p in joined ]
        indices = [ p[1] for p in joined ]

    if not m:
        m = len(p_values)
    if m <= 0 or not p_values:
        return []

    if dependent: # correct q for dependent tests
        k = c[m-1] if m <= len(c) else math.log(m) + 0.57721566490153286060651209008240243104215933593992
        m = m * k

    tmp_fdrs = [p*m/(i+1.0) for (i, p) in enumerate(p_values)]
    fdrs = []
    cmin = tmp_fdrs[-1]
    for f in reversed(tmp_fdrs):
        cmin = min(f, cmin)
        fdrs.append( cmin)
    fdrs.reverse()

    if not ordered:
        new = [ None ] * len(fdrs)
        for v,i in zip(fdrs, indices):
            new[i] = v
        fdrs = new

    return fdrs

def Bonferroni(p_values, m=None):
    """
    `Bonferroni correction <http://en.wikipedia.org/wiki/Bonferroni_correction>`_ correction on a list of p-values.

    :param p_values: a list of p-values.
    :param m: number of hypotheses tested (default ``len(p_values)``).
    """
    if not m:
        m = len(p_values)
    if m == 0:
        return []
    m = float(m)
    return [p/m for p in p_values]
