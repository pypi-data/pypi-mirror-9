"""State for the AD1D solver (:mod:`fluidsim.solvers.ad1d.state`)
=======================================================================
"""


from fluidsim.base.state import StateBase

from fluiddyn.util import mpi


class StateAD1D(StateBase):
    """Contains the variables corresponding to the state and handles the
    access to other fields for the solver AD1D.

    """

    @staticmethod
    def _complete_info_solver(info_solver):
        """Complete the ContainerXML info_solver.

        This is a static method!
        """
        info_solver.classes.State.set_attribs({
            'keys_state_phys': ['s'],
            'keys_computable': [],
            'keys_phys_needed': ['s'],
            'keys_linear_eigenmodes': ['s']
        })

    def compute(self, key, SAVE_IN_DICT=True, RAISE_ERROR=True):
        it = self.sim.time_stepping.it
        if (key in self.vars_computed
                and it == self.it_computed[key]):
            return self.vars_computed[key]

        if key == 'dx_s':
            result = self.oper.grad(self.state_phys['s'])

        else:
            to_print = 'Do not know how to compute "'+key+'".'
            if RAISE_ERROR:
                raise ValueError(to_print)
            else:
                if mpi.rank == 0:
                    print(to_print
                          + '\nreturn an array of zeros.')

                result = self.oper.constant_arrayX(value=0.)

        if SAVE_IN_DICT:
            self.vars_computed[key] = result
            self.it_computed[key] = it

        return result
