

import numpy as np

from fluidsim.base.output import OutputBase


class Output(OutputBase):

    @staticmethod
    def _complete_info_solver(info_solver):
        """Complete the ContainerXML info_solver.

        This is a static method!
        """
        info_solver.classes.Output.set_child('classes')
        classes = info_solver.classes.Output.classes

        base_name_mod = 'fluidsim.solvers.ad1d.output'

        classes.set_child(
            'PrintStdOut',
            attribs={'module_name': base_name_mod+'.print_stdout',
                     'class_name': 'PrintStdOutAD1D'})

        classes.set_child(
            'PhysFields',
            attribs={'module_name': 'fluidsim.base.output.phys_fields',
                     'class_name': 'PhysFieldsBase1D'})

    @staticmethod
    def _complete_params_with_default(params, info_solver):
        """This static method is used to complete the *params* container.
        """
        OutputBase._complete_params_with_default(params, info_solver)

        params.output.phys_fields.field_to_plot = 's'

    def compute_energy(self):
        return 0.5*np.mean(self.sim.state.state_phys['s']**2)
