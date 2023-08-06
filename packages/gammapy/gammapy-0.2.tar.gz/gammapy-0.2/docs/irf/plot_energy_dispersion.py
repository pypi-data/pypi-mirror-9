"""Plot energy dispersion example."""
import numpy as np
import matplotlib.pyplot as plt
from gammapy import irf

ebounds = np.logspace(-1, 2, 100)
pdf_matrix = irf.gauss_energy_dispersion_matrix(ebounds, sigma=0.2)
energy_dispersion = irf.EnergyDispersion(pdf_matrix, ebounds)

energy_dispersion.plot(type='matrix')
plt.show()
