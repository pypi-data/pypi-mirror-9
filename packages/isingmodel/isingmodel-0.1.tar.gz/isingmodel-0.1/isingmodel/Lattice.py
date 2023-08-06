import numpy as np
import random

class Lattice:
  def __init__(self, size=100):
    self.size = size
    self.init_lattice()

  def init_lattice(self):
    self.configuration = np.random.choice([-1,1], size=self.size**2)

  def get_grid(self):
    config = np.array(self.configuration)
    configuration_grid = config.reshape((self.size, self.size))
    return configuration_grid

  def get_neighbours(self, i):
    max_i = self.get_length() - 1
    L = self.get_length()

    if i <= max_i:
      return [(i-1)%max_i, (i+1)%max_i, (i-L)%max_i, (i+L)%max_i]

  def get_length(self):
    return self.size**2

  def get_spin(self, i):
    try:
      return self.configuration[i]
    except KeyError:
      return

  def flip_spin(self, i):
    try:
      self.configuration[i] = -self.configuration[i]
    except KeyError:
      return

  def get_new_cluster(self, new_cluster, cluster, prob):
    new = {}
    for i in new_cluster:
      spin = self.get_spin(i)
      neighbours = self.get_neighbours(i)

      random_num = random.random

      for n in neighbours:
        if self.get_spin(n) == spin:
          if random_num() < prob:
            try:
              if cluster[n]:
                pass
            except KeyError:
              new[n] = spin
    return new
