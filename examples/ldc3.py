import numpy

import matplotlib.pyplot as plt

from fvm import TimeIntegration
from fvm import Interface
from fvm import utils

def main():
    ''' An example of performing a "poor man's continuation" for a 2D lid-driven cavity using time integration'''
    dim = 2
    dof = 3
    nx = 16
    ny = nx
    nz = 1
    n = dof * nx * ny * nz

    # Define a point of interest
    poi = (nx // 2 - 1, ny // 4 - 1)

    # Define the problem
    parameters = {'Problem Type': 'Lid-driven cavity',
                  # Problem parameters
                  'Reynolds Number': 0,
                  'Lid Velocity': 1,
                  # Use a stretched grid
                  'Grid Stretching Factor': 1.5,
                  # Set a maximum step size ds
                  'Maximum Step Size': 500,
                  # Give back extra output (this is also more expensive)
                  'Verbose': True,
                  # Value describes the value that is traced in the continuation
                  # and time integration methods
                  'Value': lambda x: utils.create_state_mtx(x, nx, ny, nz, dof)[poi[0], poi[1], 0, 0],
                  'Theta': 1}

    interface = Interface(parameters, nx, ny, nz, dim, dof)

    print('Looking at point ({}, {})'.format(interface.discretization.x[poi[0]],
                                             interface.discretization.y[poi[1]]))

    x = numpy.random.random(n)

    mu_list = []
    value_list = []

    for mu in range(0, 100, 10):
        interface.set_parameter('Reynolds Number', mu)
        time_integration = TimeIntegration(interface, parameters)
        x, t, data = time_integration.integration(x, 1, 10)

        # Plot the traced value during the time integration
        # plt.plot(data.t, data.value)
        # plt.show()

        mu_list.append(mu)
        value_list.append(data.value[-1])

    # Plot a bifurcation diagram
    plt.plot(mu_list, value_list)
    plt.show()


if __name__ == '__main__':
    main()
