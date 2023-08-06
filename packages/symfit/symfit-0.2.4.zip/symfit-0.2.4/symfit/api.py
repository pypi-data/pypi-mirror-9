# Overwrite behavior of sympy objects to make more sense for this project.
import symfit.core.operators

# Expose useful objects.
from symfit.core.fit import Fit, FitResults, Maximize, Minimize, Likelihood, LeastSquares
from symfit.core.argument import Variable, Parameter

# Expose the sympy API
from sympy import *