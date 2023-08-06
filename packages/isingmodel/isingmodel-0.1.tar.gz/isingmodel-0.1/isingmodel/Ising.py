import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math
import sys
from isingmodel import Lattice

class IsingResource:
  def __init__(self, size=100, temp=300, J=1, kb=1):
    self.size = size
    self.temp = temp
    self.J = J
    self.kb = kb

  def __enter__(self):
    class Ising:
      def __init__(self, size=100, temp=300, J=1, kb=1):
        self.lattice = Lattice(size)
        self.temp = temp
        self.J = J
        self.kb = kb
        self.size = size
        self.spins = size**2
        self.magnetization = []

      def init_simulation(self, runs=10):
        self.runs = runs
        self.magnetization = np.zeros(runs)
        self.lattice.init_lattice()

      def simulate_metropolis(self, runs=10):
        self.simulate(runs, self.do_metropolis)

      def simulate_wolff(self, runs=10):
        self.simulate(runs, self.do_wolff, self.init_wolff)

      def simulate(self, runs, simulation, init=False):
        self.init_simulation(runs)
        if init:
          init()
        measure = self.measure_magnetization
        while runs > 0:
          simulation()
          self.magnetization[self.runs - runs] = measure()
          self.show_cli_progress(self.runs - runs)
          runs = runs - 1

        self.init_plots()
        self.show_results()

      def init_wolff(self):
        self.prob = 1 - math.exp(-2*self.J/(self.kb*self.temp))

      def do_wolff(self):
        start = self.pick_random_site()
        cluster = {}
        new = {}
        new[start] = self.lattice.get_spin(start)
        while True:
          new = self.lattice.get_new_cluster(new, cluster, self.prob)
          if len(new) == 0:
            break
          else:
            cluster.update(new)

        self.flip_cluster(cluster)

      def do_metropolis(self):
        site = self.pick_random_site()
        dE = self.calculate_energy_difference(site)
        prob = min(1, math.exp(-dE/(self.kb*self.temp)))
        if random.random() < prob:
          self.lattice.flip_spin(site)

      def calculate_energy_difference(self, i):
        energy = 2*self.J*self.lattice.get_spin(i)
        neighbours = self.lattice.get_neighbours(i)
        neighbour_spins = [self.lattice.get_spin(n) for n in neighbours]
        return energy*sum(neighbour_spins)

      def pick_random_site(self):
        return random.randint(0, self.lattice.get_length()-1)

      def flip_cluster(self, cluster):
        flip_spin = self.lattice.flip_spin
        for i in cluster:
          flip_spin(i)

      def measure_magnetization(self):
        return float(sum(self.lattice.configuration))/float(self.spins)

      def init_plots(self):
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(2,2,1)
        self.ax2 = self.fig.add_subplot(2,2,2)
        self.ax3 = self.fig.add_subplot(2,2,3)

        self.ax2.set_xlim(0, self.runs)
        self.ax2.set_ylim(-1, 1)
        self.ax3.set_xlim(0, self.runs)
        self.ax3.set_ylim(0, 1)

        self.im1 = self.ax1.imshow(self.lattice.get_grid())
        self.line1 = Line2D([], [], color='black')
        self.ax2.add_line(self.line1)

        self.line2 = Line2D([], [], color='black')
        self.ax3.add_line(self.line2)

        try:
          mng = plt.get_current_fig_manager()
          mng.resize(*mng.window.maxsize())
        except:
          pass

        plt.show(block=False)

      def show_results(self):
        self.im1.set_data(self.lattice.get_grid())
        self.line1.set_data(xrange(0, self.runs), self.magnetization)
        self.line2.set_data(xrange(0, self.runs), [abs(x) for x in self.magnetization])
        plt.draw()
        plt.show()

      def show_cli_progress(self, iteration):
        percent = float(iteration) / self.runs
        hashes = '#' * int(round(percent * 20))
        spaces = ' ' * (20 - len(hashes))
        sys.stdout.write("\rProgress: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
        sys.stdout.flush()

      def cleanup(self):
        print '\r\n'

    self.ising_obj = Ising(self.size, self.temp, self.J, self.kb)
    return self.ising_obj

  def __exit__(self, type, value, traceback):
    self.ising_obj.cleanup()

if __name__ == "__main__":
  with IsingResource(40, 0.1) as ising:
    ising.simulate_wolff(1000)

