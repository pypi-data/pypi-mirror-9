"""
The minimize module handles helper routines for equilibrium calculation.
"""
from __future__ import division
import pycalphad.variables as v
import scipy.spatial.distance
from sympy.utilities import default_sort_key
from sympy.utilities.lambdify import lambdify
from sympy.printing.lambdarepr import LambdaPrinter, NumExprPrinter
from sympy import Piecewise
import numpy as np
import operator
import functools
import itertools
import collections
from math import log, floor, ceil, fmod, sqrt
try:
    set
except NameError:
    from sets import Set as set #pylint: disable=W0622

_NUMEXPR = None
try:
    from importlib import import_module
    _NUMEXPR = import_module('numexpr')
except ImportError:
    pass

class NumPyPrinter(LambdaPrinter): #pylint: disable=R0903
    """
    Special numpy lambdify printer which handles vectorized
    piecewise functions.
    """
    #pylint: disable=C0103,W0232
    def _print_seq(self, seq, delimiter=', '):
        "simplified _print_seq taken from pretty.py"
        svx = [self._print(item) for item in seq]
        if svx:
            return delimiter.join(svx)
        else:
            return ""

    def _print_Piecewise(self, expr):
        "Piecewise function printer"
        expr_list = []
        cond_list = []
        for arg in expr.args:
            expr_list.append(self._print(arg.expr))
            cond_list.append(self._print(arg.cond))
        exprs = '['+','.join(expr_list)+']'
        conds = '['+','.join(cond_list)+']'
        return 'select('+conds+', '+exprs+')'

    def _print_And(self, expr):
        "Logical And printer"
        return self._print_Function(expr)

    def _print_Or(self, expr):
        "Logical Or printer"
        return self._print_Function(expr)

    def _print_Function(self, e):
        "Function printer"
        return "%s(%s)" % (e.func.__name__, self._print_seq(e.args))

class SpecialNumExprPrinter(NumExprPrinter): #pylint: disable=R0903
    "numexpr printing for vectorized piecewise functions"
    #pylint: disable=C0103,W0232
    def _print_And(self, expr):
        "Logical And printer"
        result = ['(']
        for arg in sorted(expr.args, key=default_sort_key):
            result.extend(['(', self._print(arg), ')'])
            result.append(' & ')
        result = result[:-1]
        result.append(')')
        return ''.join(result)

    def _print_Or(self, expr):
        "Logical Or printer"
        result = ['(']
        for arg in sorted(expr.args, key=default_sort_key):
            result.extend(['(', self._print(arg), ')'])
            result.append(' | ')
        result = result[:-1]
        result.append(')')
        return ''.join(result)

    def _print_Piecewise(self, expr, **kwargs):
        "Piecewise function printer"
        e, cond = expr.args[0].args
        if len(expr.args) == 1:
            return 'where(%s, %s, %f)' % (self._print(cond, **kwargs),
                                          self._print(e, **kwargs), 0)
        return 'where(%s, %s, %s)' % (self._print(cond, **kwargs),
                                      self._print(e, **kwargs),
                                      self._print(Piecewise(*expr.args[1:]), \
                                      **kwargs))

def walk(num_dims, samples_per_dim):
    """
    A generator that returns lattice points on an n-simplex.
    """
    max_ = samples_per_dim + num_dims - 1
    for cvx in itertools.combinations(range(max_), num_dims):
        cvx = list(cvx)
        yield [(y - x - 1) / (samples_per_dim - 1)
               for x, y in zip([-1] + cvx, cvx + [max_])]

def _primes(upto):
    """
    Return all prime numbers up to `upto`.
    Reference: http://rebrained.com/?p=458
    """
    primes = np.arange(3, upto+1, 2)
    isprime = np.ones((upto-1)/2, dtype=bool)
    for factor in primes[:int(sqrt(upto))]:
        if isprime[(factor-2)/2]:
            isprime[(factor*3-2)/2::factor] = 0
    return np.insert(primes[isprime], 0, 2)

def halton(dim, nbpts):
    """
    Generate `nbpts` points of the `dim`-dimensional Halton sequence.
    Originally written in C by Sebastien Paris; translated to Python by
    Josef Perktold.
    """
    #pylint: disable=C0103
    h = np.empty(nbpts * dim)
    h.fill(np.nan)
    p = np.empty(nbpts)
    p.fill(np.nan)
    P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    if dim > len(P):
        # For high-dimensional sequences, apply prime-number theorem to
        # generate additional primes
        P = _primes(int(dim * np.log(dim)))
    lognbpts = log(nbpts + 1)
    for i in range(dim):
        b = P[i]
        n = int(ceil(lognbpts / log(b)))
        for t in range(n):
            p[t] = pow(b, -(t + 1))

        for j in range(nbpts):
            d = j + 1
            sum_ = fmod(d, b) * p[0]
            for t in range(1, n):
                d = floor(d / b)
                sum_ += fmod(d, b) * p[t]

            h[j*dim + i] = sum_

    return h.reshape(nbpts, dim)

def point_sample(comp_count, pdof=10):
    """
    Sample 'pdof * (sum(comp_count) - len(comp_count))' points in
    composition space for the sublattice configuration specified
    by 'comp_count'. Points are sampled quasi-randomly from a Halton sequence.
    A Halton sequence is like a uniform random distribution, but the
    result will always be the same for a given 'comp_count' and 'size'.
    Note: For systems with only one component, only one point will be
        returned, regardless of 'pdof'. This is because the degrees of freedom
        are zero for that case.

    Parameters
    ----------
    comp_count : list
        Number of components in each sublattice.
    pdof : int
        Number of points to sample per degree of freedom.

    Returns
    -------
    ndarray of generated points satisfying the mass balance.

    Examples
    --------
    >>> comps = [8,1] # 8 components in sublattice 1; only 1 in sublattice 2
    >>> pts = point_sample(comps, pdof=20) # 7 d.o.f, returns a 140x7 ndarray
    """
    # Generate Halton sequence with appropriate dimensions and size
    pts = halton(sum(comp_count), pdof * (sum(comp_count) - len(comp_count)))
    # Convert low-discrepancy sequence to normalized exponential
    # This will be uniformly distributed over the simplices
    pts = -np.log(pts)
    cur_idx = 0
    for ctx in comp_count:
        end_idx = cur_idx + ctx
        pts[:, cur_idx:end_idx] /= pts[:, cur_idx:end_idx].sum(axis=1)[:, None]
        cur_idx = end_idx

    if len(pts) == 0:
        pts = np.atleast_2d([1] * len(comp_count))
    return pts

def make_callable(model, variables, mode=None):
    """
    Take a SymPy object and create a callable function.

    Parameters
    ----------
    model, SymPy object
        Abstract representation of function
    variables, list
        Input variables, ordered in the way the return function will expect
    mode, ['numpy', 'numexpr', 'sympy'], optional
        Method to use when 'compiling' the function. SymPy mode is
        slow and should only be used for debugging. If Numexpr is installed,
        it can offer speed-ups when calling the energy function many
        times on multi-core CPUs.

    Returns
    -------
    Function that takes arguments in the same order as 'variables'
    and returns the energy according to 'model'.

    Examples
    --------
    None yet.
    """
    energy = None
    if mode is None:
        # no mode specified; use numexpr if available, otherwise numpy
        # Note: numexpr support appears to break in multi-component situations
        # See numexpr#167 on GitHub for details
        # For now, default to numpy until a solution/workaround is available
        #if _NUMEXPR:
        #    mode = 'numexpr'
        #else:
        #    mode = 'numpy'
        mode = 'numpy'

    if mode == 'sympy':
        energy = lambda *vs: model.subs(zip(variables, vs)).evalf()
    elif mode == 'numpy':
        logical_np = [{'And': np.logical_and, 'Or': np.logical_or}, 'numpy']
        energy = lambdify(tuple(variables), model, dummify=True,
                          modules=logical_np, printer=NumPyPrinter)
    elif mode == 'numexpr':
        energy = lambdify(tuple(variables), model, dummify=True,
                          modules='numexpr', printer=SpecialNumExprPrinter)
    else:
        energy = lambdify(tuple(variables), model, dummify=True,
                          modules=mode)

    return energy

def check_degenerate_phases(phase_compositions, mindist=0.5):
    """
    Because the global minimization procedure returns a simplex as an
    output, our starting point will always assume the maximum number of
    phases. In many cases, one or more of these phases will be redundant,
    i.e., the simplex is narrow. These redundant or degenerate phases can
    be eliminated from the computation.

    Here we perform edge-wise comparisons of all the simplex vertices.
    Vertices which are from the same phase and "sufficiently" close to
    each other in composition space are redundant, and one of them is
    eliminated from the computation.

    This function accepts a DataFrame of the estimated phase compositions
    and returns the indices of the "independent" phases in the DataFrame.
    """
    output_vertices = set(range(len(phase_compositions)))
    edges = list(itertools.combinations(output_vertices, 2))
    sitefrac_columns = \
        [c for c in phase_compositions.columns.values \
            if str(c).startswith('X')]
    for edge in edges:
        # check if both end-points are still in output_vertices
        # if not, we should skip this edge
        if not set(edge).issubset(output_vertices):
            continue
        first_vertex = phase_compositions.iloc[edge[0]]
        second_vertex = phase_compositions.iloc[edge[1]]
        if first_vertex.loc['Phase'] != second_vertex.loc['Phase']:
            # phases along this edge do not match; leave them alone
            continue
        # phases match; check the distance between their respective
        # site fractions; if below the threshold, eliminate one of them
        first_coords = first_vertex.loc[sitefrac_columns].fillna(0)
        second_coords = second_vertex.loc[sitefrac_columns].fillna(0)
        edge_length = \
            scipy.spatial.distance.chebyshev(first_coords, second_coords)
        if edge_length < mindist and len(output_vertices) > 1:
            output_vertices.discard(edge[1])
    return list(output_vertices)

def generate_dof(phase, active_comps):
    """
    Accept a Phase object and a set() of the active components.
    Return a tuple of variable names and the sublattice degrees of freedom.
    """
    variables = []
    sublattice_dof = []
    for idx, sublattice in enumerate(phase.constituents):
        dof = 0
        for component in sorted(set(sublattice).intersection(active_comps)):
            variables.append(v.SiteFraction(phase.name.upper(), idx, component))
            dof += 1
        sublattice_dof.append(dof)
    return variables, sublattice_dof

def endmember_matrix(dof, vacancy_indices=None):
    """
    Accept the number of components in each sublattice.
    Return a matrix corresponding to the compositions of all endmembers.

    Parameters
    ==========
    dof : list of int
        Number of components in each sublattice.
    vacancy_indices, list of int, optional
        If vacancies are present in every sublattice, specify their indices
        in each sublattice to ensure the "pure vacancy" endmember is excluded.

    Examples
    ========
    Sublattice configuration like: (AL, NI, VA):(AL, NI, VA):(VA)
    >>> endmember_matrix([3,3,1], vacancy_indices=[2, 2, 0])
    """
    total_endmembers = functools.reduce(operator.mul, dof, 1)
    res_matrix = np.empty((total_endmembers, sum(dof)), dtype=np.float)
    dof_arrays = [np.eye(d).tolist() for d in dof]
    row_idx = 0
    for row in itertools.product(*dof_arrays):
        res_matrix[row_idx, :] = np.concatenate(row, axis=0)
        row_idx += 1
    if vacancy_indices is not None and len(vacancy_indices) == len(dof):
        dof_adj = np.array([sum(dof[0:i]) for i in range(len(dof))])
        indices = np.array(vacancy_indices) + dof_adj
        row_idx_to_delete = np.where(np.all(res_matrix[:, indices] == 1,
                                            axis=1))
        res_matrix = np.delete(res_matrix, (row_idx_to_delete), axis=0)
    return res_matrix

def unpack_kwarg(kwarg_obj, default_arg=None):
    """
    Keyword arguments in pycalphad can be passed as a constant value, a
    dict of phase names and values, or a list containing both of these. If
    the latter, then the dict is checked first; if the phase of interest is not
    there, then the constant value is used.

    This function is a way to construct defaultdicts out of keyword arguments.

    Parameters
    ==========
    kwarg_obj : dict, iterable, or None
        Argument to unpack into a defaultdict
    default_arg : object
        Default value to use if iterable isn't specified

    Returns
    =======
    defaultdict for the keyword argument of interest

    Examples
    ========
    >>> test_func = lambda **kwargs: print(unpack_kwarg('opt'))
    >>> test_func(opt=100)
    >>> test_func(opt={'FCC_A1': 50, 'BCC_B2': 10})
    >>> test_func(opt=[{'FCC_A1': 30}, 200])
    >>> test_func()
    >>> test_func2 = lambda **kwargs: print(unpack_kwarg('opt', default_arg=1))
    >>> test_func2()
    """
    new_dict = collections.defaultdict(lambda: default_arg)

    if isinstance(kwarg_obj, collections.Mapping):
        new_dict.update(kwarg_obj)
    # kwarg_obj is a list containing a dict and a default
    elif isinstance(kwarg_obj, collections.Iterable):
        for element in kwarg_obj:
            if isinstance(element, collections.Mapping):
                new_dict.update(element)
            else:
                # element=element syntax to silence var-from-loop warning
                new_dict = collections.defaultdict(
                    lambda element=element: element, new_dict)
    elif kwarg_obj is None:
        pass
    else:
        new_dict = collections.defaultdict(lambda: kwarg_obj)

    return new_dict
