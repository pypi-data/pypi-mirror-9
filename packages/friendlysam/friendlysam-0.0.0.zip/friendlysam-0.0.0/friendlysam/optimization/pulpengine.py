# -*- coding: utf-8 -*-

from friendlysam.log import get_logger
logger = get_logger(__name__)

import operator
import collections
from itertools import chain

from pulp import *

from friendlysam.optimization import (
    Problem, Variable, Constraint, Relation, SOS1, SOS2, Maximize, Minimize, Domain, SolverError)

def _cbc_solve(problem):
    solver = PULP_CBC_CMD()
    return solver.solve_CBC(problem, use_mps=False)

DEFAULT_OPTIONS = dict(
    solver_order=[
        GUROBI_CMD(msg=0).solve,
        _cbc_solve
    ])

_domain_mapping = {
    Domain.real: LpContinuous,
    Domain.integer: LpInteger,
    Domain.binary: LpBinary,
    None: None
}

_pulp_statuses = {
    LpStatusNotSolved: 'LpStatusNotSolved',
    LpStatusOptimal: 'LpStatusOptimal',
    LpStatusInfeasible: 'LpStatusInfeasible',
    LpStatusUnbounded: 'LpStatusUnbounded',
    LpStatusUndefined: 'LpStatusUndefined'
}

class PulpSolver(object):
    """docstring for PulpSolver"""

    def __init__(self):
        super().__init__()
        self.options = DEFAULT_OPTIONS
        self._names = set()

    def _get_unique_name(self, name=None):
        _counter = 0
        while _counter == 0 or name in self._names:
            _counter += 1
            name = 'x{}'.format(_counter)

        self._names.add(name)
        return name

    def _make_pulp_var(self, variable):
        options = dict(
            lowBound=variable.lb,
            upBound=variable.ub,
            cat=_domain_mapping[variable.domain])

        name = self._get_unique_name(variable.name)

        return LpVariable(name, **options)

    def solve(self, problem):
        pulp_vars = {v: self._make_pulp_var(v) for v in problem.variables if not hasattr(v, 'value')}

        if isinstance(problem.objective, Minimize):
            sense = LpMinimize
        elif isinstance(problem.objective, Maximize):
            sense = LpMaximize
        model = LpProblem('friendlysam', sense)
        
        model += problem.objective.expr.evaluate(replacements=pulp_vars)

        for i, c in enumerate(problem.constraints):
            if isinstance(c, Constraint):
                model += c.expr.evaluate(replacements=pulp_vars)
                
            elif isinstance(c, (SOS1, SOS2)):
                if isinstance(c, SOS1):
                    sosdict = model.sos1
                elif isinstance(c, SOS2):
                    sosdict = model.sos2
                else:
                    raise NotImplementedError()

                weights = list(range(1, len(c.variables)+1))
                constr_name = 'sosconstr{}'.format(i)
                sosdict[constr_name] = {pulp_vars[v]: w for v, w in zip(c.variables, weights)}

            else:
                raise NotImplementedError('Cannot handle constraint {}'.format(c))

        exceptions = []
        for solver_func in self.options['solver_order']:
            try:
                status = solver_func(model)
                break
            except Exception as e:
                exceptions.append({'solver': solver_func, 'exception': str(e)})
        else:
            raise RuntimeError('None of the solvers worked. More info: {}'.format(exceptions))
        
        if not status == LpStatusOptimal:
            raise SolverError("pulp solution status is '{0}'".format(_pulp_statuses[status]))

        for e in exceptions:
            print(e)

        return {v: pv.value() for v, pv in pulp_vars.items()}
