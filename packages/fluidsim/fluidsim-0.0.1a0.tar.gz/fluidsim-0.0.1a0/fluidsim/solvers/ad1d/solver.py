"""AD1D solver (:mod:`fluidsim.solvers.ad1d.solver`)
=========================================================

.. currentmodule:: fluidsim.solvers.ad1d.solver

Provides:

.. autoclass:: Simul
   :members:
   :private-members:


"""

from fluidsim.base.solvers.base import SimulBase
from fluidsim.operators.setofvariables import SetOfVariables
from fluidsim.base.solvers.finite_diff import InfoSolverFiniteDiff


info_solver = InfoSolverFiniteDiff()

package = 'fluidsim.solvers.ad1d'
info_solver.module_name = package + '.solver'
info_solver.class_name = 'Simul'
info_solver.short_name = 'AD1D'

classes = info_solver.classes

classes.State.module_name = package + '.state'
classes.State.class_name = 'StateAD1D'

classes.InitFields.module_name = package + '.init_fields'
classes.InitFields.class_name = 'InitFieldsAD1D'

classes.Output.module_name = package + '.output'
classes.Output.class_name = 'Output'

# classes.Forcing.module_name = package + '.forcing'
# classes.Forcing.class_name = 'ForcingAD1D'


info_solver.complete_with_classes()


class Simul(SimulBase):
    r"""Advection-diffusion solver 1D.

    Notes
    -----

    .. |p| mathmacro:: \partial

    We use a finite difference method with the Crank-Nicolson time
    scheme to solve the equation

    .. math:: \p_t s + U \p_x s = D(s),

    where :math:`d(s)` is the dissipation term and :math:`U` is a
    constant velocity.

    """

    @staticmethod
    def _complete_params_with_default(params):
        """This static method is used to complete the *params* container.
        """
        SimulBase._complete_params_with_default(params)
        attribs = {'U': 1.}
        params.set_attribs(attribs)

    def __init__(self, params):
        # the common initialization with the AD1D info_solver:
        super(Simul, self).__init__(params, info_solver)

    def tendencies_nonlin(self, state_phys=None):
        """Compute the "nonlinear" tendencies."""
        tendencies = SetOfVariables(
            like_this_sov=self.state.state_phys,
            name_type_variables='tendencies', value=0.)

        if self.params.FORCING:
            tendencies += self.forcing.tendencies

        return tendencies

    def linear_operator(self):
        """Compute the linear operator as a matrix."""

        return (- self.params.U*self.oper.sparse_px
                + self.params.nu_2*(self.oper.sparse_pxx))


if __name__ == "__main__":

    import fluiddyn as fld

    params = fld.simul.create_params(info_solver)

    params.U = 1.

    params.short_name_type_run = 'test'

    params.oper.nx = 200
    params.oper.Lx = 1.

    # params.oper.type_fft = 'FFTWPY'

    params.time_stepping.type_time_scheme = 'RK2'

    # delta_x = params.oper.Lx/params.oper.nx
    params.nu_2 = 0.01

    params.time_stepping.t_end = 0.4
    params.time_stepping.USE_CFL = True
    # params.time_stepping.deltat0 = 0.1

    params.init_fields.type_flow_init = 'GAUSSIAN'

    params.output.periods_print.print_stdout = 0.25

    params.output.periods_save.phys_fields = 0.5

    params.output.periods_plot.phys_fields = 0.

    params.output.phys_fields.field_to_plot = 's'

    # params.output.spectra.has_to_plot = 1  # False
    # params.output.spatial_means.has_to_plot = 1  # False
    # params.output.spect_energy_budg.has_to_plot = 1  # False
    # params.output.increments.has_to_plot = 1  # False

    sim = Simul(params)

    # sim.output.phys_fields.plot()
    sim.time_stepping.start()

    print 'x of s_max: ', sim.oper.xs[sim.state.state_phys.data.argmax()]

    sim.output.phys_fields.plot()

    fld.show()
