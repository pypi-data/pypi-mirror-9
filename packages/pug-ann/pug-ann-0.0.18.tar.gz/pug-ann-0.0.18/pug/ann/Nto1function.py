from pybrain.utilities import setAllArgs
__author__ = 'Tom Schaul, tom@idsia.ch'

from scipy import zeros, array, ndarray

# from pybrain.rl.environments import Environment
from pybrain.rl.environments.functions.function import FunctionEnvironment 
from pybrain.structure.parametercontainer import ParameterContainer
# from pybrain.rl.environments.fitnessevaluator import FitnessEvaluator


class SmartSpenderFunctionEnvironment(FunctionEnvironment):
    """ An N-to-1 mapping with a single goal or minimum of value of zero, at xopt. """

    # what input dimensions can the function have?
    xdimMin = 1
    xdimMax = None
    xdim = None

    # the (single) point where f = 0
    xopt = None

    # what would be the desired performance? by default: something close to zero
    desiredValue = 1e-10
    toBeMinimized = True
    
    # does the function already include a penalization term, to keep search near the origin?
    penalized = False

    def __init__(self, price_dataframe, wallet_reset_period='day', performance_reset_period='month', xdim=None, xopt=None, xbound=1, feasible=True, constrained=False, violation=False, **args):
        self.feasible=feasible
        self.constrained=constrained
        self.violation=violation
        self.xbound=xbound
        if xdim is None:
            xdim = self.xdim
        if xdim is None:
            xdim = self.xdimMin
        assert xdim >= self.xdimMin and not (self.xdimMax is not None and xdim > self.xdimMax)
        self.xdim = xdim
        if xopt is None:
            self.xopt = zeros(self.xdim)
        else:
            self.xopt = xopt
        setAllArgs(self, args)
        self.reset()

    def __call__(self, x):
        if isinstance(x, ParameterContainer):
            x = x.params
        assert type(x) == ndarray, 'FunctionEnvironment: Input not understood: '+str(type(x))
        return self.f(x)

    # methods for conforming to the Environment interface:
    def reset(self):
        self.result = None

    def getSensors(self):
        """ The one sensor is the function result. """
        tmp = self.result
        assert tmp is not None
        self.result = None
        return array([tmp])

    def performAction(self, action):
        """ The action argument is a numpy array of values for the function inputs. 

        Activate
        """
        self.result = self(action)

    @property
    def indim(self):
        return self.xdim

    # does not provide any observations
    outdim = 0

