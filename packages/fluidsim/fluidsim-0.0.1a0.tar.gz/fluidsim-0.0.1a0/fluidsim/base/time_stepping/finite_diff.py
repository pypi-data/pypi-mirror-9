"""Time stepping (:mod:`fluidsim.base.time_stepping.finite_diff`)
=======================================================================

.. currentmodule:: fluidsim.base.time_stepping.finite_diff

Provides:

.. autoclass:: TimeSteppingFiniteDiffCrankNicolson
   :members:
   :private-members:

"""

import numpy as np
import scipy.sparse as sparse
from scipy.sparse.linalg import spsolve

from copy import deepcopy

from fluidsim.operators.setofvariables import SetOfVariables

from .base import TimeSteppingBase


class TimeSteppingFiniteDiffCrankNicolson(TimeSteppingBase):
    """
    Time stepping class for finite-difference solvers.

    """
    def __init__(self, sim):
        self.params = sim.params
        self.sim = sim

        self.it = 0
        self.t = 0

        # self._init_freq_lin()
        self._init_compute_time_step()
        self._init_time_scheme()

        self.L = sim.linear_operator()
        self.set_of_vars_temp = SetOfVariables(
            like_this_sov=sim.state.state_phys)

    def one_time_step_computation(self):
        """One time step"""
        self._time_step_RK()
        self.t += self.deltat
        self.it += 1
        if np.isnan(np.min(self.sim.state.state_phys.data)):
            raise ValueError(
                'nan at it = {0}, t = {1:.4f}'.format(self.it, self.t))

    def _time_step_RK2(self):
        r"""Advance in time the variables with the Runge-Kutta 2 method.

        .. _rk2timeschemeFiniteDiff:

        Notes
        -----

        .. Look at Simson KTH documentation...
           (http://www.mech.kth.se/~mattias/simson-user-guide-v4.0.pdf)

        The Runge-Kutta 2 method computes an approximation of the
        solution after a time increment :math:`dt`. We denote the
        initial time :math:`t = 0`.

        For the finite difference schemes, We consider an equation of the form

        .. math:: \p_t S = L S + N(S),

        The linear term can be treated with an implicit method while
        the nonlinear term have to be treated with an explicit method
        (see for example `Explicit and implicit methods
        <http://en.wikipedia.org/wiki/Explicit_and_implicit_methods>`_).

        - Approximation 1:

          For the first step where the nonlinear term is approximated
          as :math:`N(S) \simeq N(S_0)`, we obtain

          .. math::
             \left( 1 - \frac{dt}{4} L \right) S_{A1dt/2}
             \simeq \left( 1 + \frac{dt}{4} L \right) S_0 + N(S_0)dt/2

          Once the right-hand side has been computed, a linear
          equation has to be solved. It is not efficient to invert the
          matrix :math:`1 + \frac{dt}{2} L` so other methods have to
          be used, as the `Thomas algorithm
          <http://en.wikipedia.org/wiki/Tridiagonal_matrix_algorithm>`_,
          or algorithms based on the LU or the QR decompositions.

        - Approximation 2:

            The nonlinear term is then approximated as :math:`N(S)
            \simeq N(S_{A1dt/2})`, which gives

            .. math::
               \left( 1 - \frac{dt}{2} L \right) S_{A2dt}
               \simeq \left( 1 + \frac{dt}{2} L \right) S_0 + N(S_{A1dt/2})dt

        """
        dt = self.deltat
        sim = self.sim
        identity = sparse.identity(sim.state.state_phys.data.size)

        # it seems that there is a bug with the proper RK2 method
        # (it "goes too fast")

        # # approximation 1 (at t + dt/2 -> "A1dt2"):
        # tendenciesNL_0 = sim.tendencies_nonlin()
        # rhs_A1dt2 = self.right_hand_side(sim.state.state_phys,
        #                                  tendenciesNL_0, dt/2)

        # A_A1dt2 = identity - dt/4*self.L
        # S_A1dt2 = self.invert_to_get_solution(A_A1dt2, rhs_A1dt2)
        # del(rhs_A1dt2, A_A1dt2)

        # # approximation 2 (at t + dt -> "A2dt"):
        # tendenciesNL_1 = sim.tendencies_nonlin(S_A1dt2)
        # rhs_A2dt = self.right_hand_side(S_A1dt2, tendenciesNL_1, dt)
        # A_A2dt = identity - dt/2*self.L
        # sim.state.state_phys = deepcopy(
        #     self.invert_to_get_solution(A_A2dt, rhs_A2dt))

        # it seems to work with the basic Newton time stepping:
        tendenciesNL_0 = sim.tendencies_nonlin()
        rhs_A1dt = self.right_hand_side(sim.state.state_phys,
                                        tendenciesNL_0, dt)
        A_A1dt = identity - dt/2*self.L
        sim.state.state_phys = deepcopy(
            self.invert_to_get_solution(A_A1dt, rhs_A1dt))

    def right_hand_side(self, S, N, dt):
        return (S.data.ravel()
                + dt/2*self.L.dot(S.data.flat)
                + dt*N.data.ravel())

    def invert_to_get_solution(self, A, b):
        """Solve the linear system :math:`Ax = b`."""
        self.set_of_vars_temp.data = spsolve(A, b).reshape(
            self.set_of_vars_temp.data.shape)
        return self.set_of_vars_temp
