import numpy
import pytest

from numpy.testing import assert_allclose

import matplotlib.pyplot as plt

from fvm import Continuation

# Import common fixtures
from test.jada_fixtures import * # noqa: F401, F403

@pytest.fixture(autouse=True, scope='module')
def import_test():
    try:
        from fvm import JadaInterface # noqa: F401
    except ImportError:
        pytest.skip('jadapy not found')

    try:
        from fvm import HYMLSInterface # noqa: F401
    except ImportError:
        pytest.skip('HYMLS not found')

@pytest.fixture(scope='module')
def interface(nx):
    from fvm import HYMLSInterface
    from PyTrilinos import Epetra
    from PyTrilinos import Teuchos

    dim = 2
    dof = 3
    ny = nx
    nz = 1

    parameters = Teuchos.ParameterList()
    parameters.set('Reynolds Number', 0)
    parameters.set('Bordered Solver', True)

    comm = Epetra.PyComm()
    interface = HYMLSInterface.Interface(comm, parameters, nx, ny, nz, dim, dof)

    return interface

@pytest.fixture(scope='module')
def x(interface):
    from fvm import HYMLSInterface

    continuation = Continuation(interface, interface.parameters)

    x0 = HYMLSInterface.Vector(interface.map)
    x0 = continuation.newton(x0)

    start = 0
    target = 2000
    ds = 100
    return continuation.continuation(x0, 'Reynolds Number', start, target, ds)[0]

def test_prec_2D(arpack_eigs, interface, x, num_evs, tol, atol, interactive=False):
    from fvm import JadaHYMLSInterface

    from jadapy import EpetraInterface
    from jadapy import jdqz

    numpy.random.seed(1234)

    jac_op = EpetraInterface.CrsMatrix(interface.jacobian(x))
    mass_op = EpetraInterface.CrsMatrix(interface.mass_matrix())
    jada_interface = JadaHYMLSInterface.JadaHYMLSInterface(interface.map, interface, preconditioned_solve=False)

    alpha, beta = jdqz.jdqz(jac_op, mass_op, num_evs, tol=tol, subspace_dimensions=[20, 40],
                            interface=jada_interface, prec=jada_interface.prec)
    jdqz_eigs = numpy.array(sorted(alpha / beta, key=lambda x: abs(x)))

    assert_allclose(jdqz_eigs.real, arpack_eigs.real, rtol=0, atol=atol)
    assert_allclose(abs(jdqz_eigs.imag), abs(arpack_eigs.imag), rtol=0, atol=atol)

    if not interactive:
        return x

    fig, ax = plt.subplots()
    ax.scatter(jdqz_eigs.real, jdqz_eigs.imag, marker='+')
    plt.show()

def test_prec_solve_2D(arpack_eigs, interface, x, num_evs, tol, atol, interactive=False):
    from fvm import JadaHYMLSInterface

    from jadapy import EpetraInterface
    from jadapy import jdqz

    numpy.random.seed(1234)

    jac_op = EpetraInterface.CrsMatrix(interface.jacobian(x))
    mass_op = EpetraInterface.CrsMatrix(interface.mass_matrix())
    jada_interface = JadaHYMLSInterface.JadaHYMLSInterface(interface.map, interface, preconditioned_solve=True)

    alpha, beta = jdqz.jdqz(jac_op, mass_op, num_evs, tol=tol, subspace_dimensions=[20, 40],
                            interface=jada_interface)
    jdqz_eigs = numpy.array(sorted(alpha / beta, key=lambda x: abs(x)))

    assert_allclose(jdqz_eigs.real, arpack_eigs.real, rtol=0, atol=atol)
    assert_allclose(abs(jdqz_eigs.imag), abs(arpack_eigs.imag), rtol=0, atol=atol)

    if not interactive:
        return x

    fig, ax = plt.subplots()
    ax.scatter(jdqz_eigs.real, jdqz_eigs.imag, marker='+')
    plt.show()

def test_complex_prec_2D(arpack_eigs, interface, x, num_evs, tol, atol, interactive=False):
    from fvm import JadaHYMLSInterface

    from jadapy import ComplexEpetraInterface
    from jadapy import jdqz

    numpy.random.seed(1234)

    jac_op = ComplexEpetraInterface.CrsMatrix(interface.jacobian(x))
    mass_op = ComplexEpetraInterface.CrsMatrix(interface.mass_matrix())
    jada_interface = JadaHYMLSInterface.ComplexJadaHYMLSInterface(interface.map, interface, preconditioned_solve=False)

    alpha, beta = jdqz.jdqz(jac_op, mass_op, num_evs, tol=tol, subspace_dimensions=[20, 40],
                            interface=jada_interface, prec=jada_interface.prec)
    jdqz_eigs = numpy.array(sorted(alpha / beta, key=lambda x: abs(x)))

    assert_allclose(jdqz_eigs.real, arpack_eigs.real, rtol=0, atol=atol)
    assert_allclose(abs(jdqz_eigs.imag), abs(arpack_eigs.imag), rtol=0, atol=atol)

    if not interactive:
        return x

    fig, ax = plt.subplots()
    ax.scatter(jdqz_eigs.real, jdqz_eigs.imag, marker='+')
    plt.show()

def test_complex_prec_solve_2D(arpack_eigs, interface, x, num_evs, tol, atol, interactive=False):
    from fvm import JadaHYMLSInterface

    from jadapy import ComplexEpetraInterface
    from jadapy import jdqz

    numpy.random.seed(1234)

    jac_op = ComplexEpetraInterface.CrsMatrix(interface.jacobian(x))
    mass_op = ComplexEpetraInterface.CrsMatrix(interface.mass_matrix())
    jada_interface = JadaHYMLSInterface.ComplexJadaHYMLSInterface(interface.map, interface, preconditioned_solve=True)

    alpha, beta = jdqz.jdqz(jac_op, mass_op, num_evs, tol=tol, subspace_dimensions=[20, 40],
                            interface=jada_interface)
    jdqz_eigs = numpy.array(sorted(alpha / beta, key=lambda x: abs(x)))

    assert_allclose(jdqz_eigs.real, arpack_eigs.real, rtol=0, atol=atol)
    assert_allclose(abs(jdqz_eigs.imag), abs(arpack_eigs.imag), rtol=0, atol=atol)

    if not interactive:
        return x

    fig, ax = plt.subplots()
    ax.scatter(jdqz_eigs.real, jdqz_eigs.imag, marker='+')
    plt.show()

def test_bordered_prec_solve_2D(arpack_eigs, interface, x, num_evs, tol, atol, interactive=False):
    from fvm import JadaHYMLSInterface

    from jadapy import EpetraInterface
    from jadapy import jdqz

    numpy.random.seed(1234)

    jac_op = EpetraInterface.CrsMatrix(interface.jacobian(x))
    mass_op = EpetraInterface.CrsMatrix(interface.mass_matrix())
    jada_interface = JadaHYMLSInterface.BorderedJadaHYMLSInterface(interface.map, interface)

    alpha, beta = jdqz.jdqz(jac_op, mass_op, num_evs, tol=tol, subspace_dimensions=[20, 40],
                            interface=jada_interface)
    jdqz_eigs = numpy.array(sorted(alpha / beta, key=lambda x: abs(x)))

    assert_allclose(jdqz_eigs.real, arpack_eigs.real, rtol=0, atol=atol)
    assert_allclose(abs(jdqz_eigs.imag), abs(arpack_eigs.imag), rtol=0, atol=atol)

    if not interactive:
        return x

    fig, ax = plt.subplots()
    ax.scatter(jdqz_eigs.real, jdqz_eigs.imag, marker='+')
    plt.show()
