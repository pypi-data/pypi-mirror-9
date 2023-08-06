
from __future__ import print_function

import os
# import numpy as np

# from time import time

from fluiddyn.util import mpi


class PrintStdOutBase(object):
    """A :class:`PrintStdOutBase` object is used to print in both the
    stdout and the stdout.txt file, and also to print simple info on
    the current state of the simulation."""

    _tag = 'print_stdout'

    @staticmethod
    def _complete_params_with_default(params):
        params.output.periods_print.set_attrib('print_stdout', 1.)

    def __init__(self, output):
        sim = output.sim
        params = sim.params

        self.output = output
        self.sim = sim
        self.params = params

        try:
            self.c2 = params.c2
            self.f = params.f
        except AttributeError:
            pass

        self.nx = params.oper.nx

        self.period_print = params.output.periods_print.print_stdout

        self.path_file = self.output.path_run+'/stdout.txt'

        if mpi.rank == 0 and self.output.has_to_save:
                if not os.path.exists(self.path_file):
                    self.file = open(self.path_file, 'w')
                else:
                    self.file = open(self.path_file, 'r+')
                    self.file.seek(0, 2)  # go to the end of the file

    def complete_init_with_state(self):

        self.energy0 = self.output.compute_energy()

        if self.period_print == 0:
            return

        self.energy_temp = self.energy0+0.
        self.t_last_print_info = -self.period_print
        self.t_real_word_last = 0.

        self.print_stdout = self.__call__

    def __call__(self, to_print, end='\n'):
        """Print in stdout and if SAVE in the file stdout.txt"""
        if mpi.rank == 0:
            print(to_print, end=end)
            if self.output.has_to_save:
                self.file.write(to_print+end)
                self.file.flush()
                os.fsync(self.file.fileno())

    def online_print(self):
        """Print simple info on the current state of the simulation"""
        tsim = self.sim.time_stepping.t
        if (tsim-self.t_last_print_info >= self.period_print):
            self.t_last_print_info = tsim
            self.print_stdout(
                'it = {0:6d} ; t = {1:10.6g} ; deltat  = {2:10.5g}\n'.format(
                    self.sim.time_stepping.it,
                    self.sim.time_stepping.t,
                    self.sim.time_stepping.deltat))

    def close(self):
        try:
            self.file.close()
        except AttributeError:
            pass
