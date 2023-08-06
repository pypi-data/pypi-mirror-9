
import numpy as np

from fluiddyn.util import mpi

from .base import SpecificOutput


def cumsum_inv(a):
    return a[::-1].cumsum()[::-1]


def inner_prod(a_fft, b_fft):
    return np.real(a_fft.conj()*b_fft)


class SpectralEnergyBudgetBase(SpecificOutput):
    """A :class:`Spectra` object handles the saving of .

    This class uses the particular functions defined by some solvers
    :func:`` and
    :func``. If the solver doesn't has these
    functions, this class does nothing.
    """

    _tag = 'spect_energy_budg'

    @staticmethod
    def _complete_params_with_default(params):
        tag = 'spect_energy_budg'

        params.output.periods_save.set_attrib(tag, 0)
        params.output.set_child(tag,
                                attribs={'HAS_TO_PLOT_SAVED': False})

    def __init__(self, output):

        params = output.sim.params
        self.nx = params.oper.nx

        self.spectrum2D_from_fft = output.sim.oper.spectrum2D_from_fft

        HAS_TO_PLOT_SAVED = params.output.spect_energy_budg.HAS_TO_PLOT_SAVED
        super(SpectralEnergyBudgetBase, self).__init__(
            output,
            name_file='spectral_energy_budget.h5',
            period_save=params.output.periods_save.spect_energy_budg,
            has_to_plot_saved=HAS_TO_PLOT_SAVED,
            dico_arrays_1time={'khE': output.sim.oper.khE})

    def compute(self):
        """compute the values at one time."""
        if mpi.rank == 0:
            dico_results = {}
            return dico_results

    def init_online_plot(self):
        width_axe = 0.85
        height_axe = 0.37
        x_left_axe = 0.12
        z_bottom_axe = 0.56

        size_axe = [x_left_axe, z_bottom_axe,
                    width_axe, height_axe]
        self.fig, axe_a = self.output.figure_axe(size_axe=size_axe,
                                                 numfig=4000000)
        self.axe_a = axe_a
        axe_a.set_xlabel('k_h')
        axe_a.set_ylabel('Pi(k_h) energy')
        axe_a.set_title('energy flux, solver ' + self.output.name_solver +
                        ', nh = {0:5d}'.format(self.nx))
        axe_a.hold(True)
        axe_a.set_xscale('log')

        z_bottom_axe = 0.08
        size_axe[1] = z_bottom_axe
        axe_b = self.fig.add_axes(size_axe)
        self.axe_b = axe_b
        axe_b.set_xlabel('k_h')
        axe_b.set_ylabel('Pi(k_h) energy')
        axe_b.hold(True)
        axe_b.set_xscale('log')

    def fnonlinfft_from_uxuy_funcfft(self, ux, uy, f_fft):
        """Compute a non-linear term."""
        oper = self.oper
        px_f_fft, py_f_fft = oper.gradfft_from_fft(f_fft)
        px_f = oper.ifft2(px_f_fft)
        py_f = oper.ifft2(py_f_fft)
        del(px_f_fft, py_f_fft)
        Fnl = -ux*px_f - uy*py_f
        del(px_f, py_f)
        Fnl_fft = oper.fft2(Fnl)
        oper.dealiasing(Fnl_fft)
        return Fnl_fft

    def fnonlinfft_from_uruddivfunc(self,
                                    urx, ury,
                                    udx, udy, div,
                                    func_fft, func):
        """Compute a non-linear term."""
        oper = self.oper
        px_func_fft, py_func_fft = oper.gradfft_from_fft(func_fft)
        px_func = oper.ifft2(px_func_fft)
        py_func = oper.ifft2(py_func_fft)
        del(px_func_fft, py_func_fft)
        Frf = -urx*px_func - ury*py_func
        Fdf = -udx*px_func - udy*py_func - div*func/2
        del(px_func, py_func)
        Frf_fft = oper.fft2(Frf)
        Fdf_fft = oper.fft2(Fdf)
        oper.dealiasing(Frf_fft, Fdf_fft)
        return Frf_fft, Fdf_fft
