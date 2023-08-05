from __future__ import division
from __future__ import print_function
from ..util import read_param_file
from sys import exit
import numpy as np
import math
from . import common_args

# Perform FAST Analysis on file of model results
# Returns a dictionary with keys 'S1' and 'ST'
# Where each entry is a list of size D (the number of parameters)
# Containing the indices in the same order as the parameter file


def analyze(problem, Y, M=4, print_to_console=False):

    D = problem['num_vars']

    if Y.size % (D) == 0:
        N = int(Y.size / D)
    else:
        print("""
            Error: Number of samples in model output file must be a multiple of D, 
            where D is the number of parameters in your parameter file.
          """)
        exit()

    # Recreate the vector omega used in the sampling
    omega = np.empty([D])
    omega[0] = math.floor((N - 1) / (2 * M))
    m = math.floor(omega[0] / (2 * M))

    if m >= (D - 1):
        omega[1:] = np.floor(np.linspace(1, m, D - 1))
    else:
        omega[1:] = np.arange(D - 1) % m + 1

    # Calculate and Output the First and Total Order Values
    if print_to_console:
        print("Parameter First Total")
    Si = dict((k, [None] * D) for k in ['S1', 'ST'])
    for i in range(D):
        l = np.arange(i * N, (i + 1) * N)
        Si['S1'][i] = compute_first_order(Y[l], N, M, omega[0])
        Si['ST'][i] = compute_total_order(Y[l], N, omega[0])
        if print_to_console:
            print("%s %f %f" %
                  (problem['names'][i], Si['S1'][i], Si['ST'][i]))
    return Si


def compute_first_order(outputs, N, M, omega):
    f = np.fft.fft(outputs)
    Sp = np.power(np.absolute(f[np.arange(1, int(N / 2))]) / N, 2)
    V = 2 * np.sum(Sp)
    D1 = 2 * np.sum(Sp[np.arange(1, M + 1) * int(omega) - 1])
    return D1 / V


def compute_total_order(outputs, N, omega):
    f = np.fft.fft(outputs)
    Sp = np.power(np.absolute(f[np.arange(1, int(N / 2))]) / N, 2)
    V = 2 * np.sum(Sp)
    Dt = 2 * sum(Sp[np.arange(int(omega / 2))])
    return (1 - Dt / V)

if __name__ == "__main__":

    parser = common_args.create()
    args = parser.parse_args()
    problem = read_param_file(args.paramfile)
    Y = np.loadtxt(args.model_output_file, delimiter=args.delimiter, usecols=(args.column,))

    analyze(problem, Y, print_to_console=True)
