# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from astropy.tests.helper import pytest
from astropy.utils.data import get_pkg_data_filename
from astropy.extern import six
import astropy.units as u

from ..analysis import save_diagnostic_plots
from ..core import run_sampler, get_sampler, uniform_prior, normal_prior

try:
    import emcee
    HAS_EMCEE = True
except ImportError:
    HAS_EMCEE = False

from astropy.io import ascii

# Read data
fname = get_pkg_data_filename('data/CrabNebula_HESS_ipac.dat')
data_table = ascii.read(fname)

# Read spectrum with symmetric flux errors
fname2 = get_pkg_data_filename('data/CrabNebula_HESS_ipac_symmetric.dat')
data_table2 = ascii.read(fname2)

# Model definition

def cutoffexp(pars, data):
    """
    Powerlaw with exponential cutoff

    Parameters:
        - 0: PL normalization
        - 1: PL index
        - 2: cutoff energy
        - 3: cutoff exponent (beta)
    """

    x = data['energy']
    # take logarithmic mean of first and last data points as normalization
    # energy
    x0 = np.sqrt(x[0] * x[-1])

    N = pars[0]
    gamma = pars[1]
    ecut = pars[2] * u.TeV
    # beta  = pars[3]
    beta = 1.

    return N * (x / x0) ** -gamma * np.exp(-(x / ecut) ** beta) * u.Unit('1/(cm2 s TeV)')

# Prior definition

def lnprior(pars):
    """
    Return probability of parameter values according to prior knowledge.
    Parameter limits should be done here through uniform prior ditributions
    """

    logprob = uniform_prior(pars[0], 0., np.inf) \
        + normal_prior(pars[1], 1.4, 0.5) \
        + uniform_prior(pars[2], 0., np.inf)

    return logprob

# Set initial parameters

p0 = np.array((1e-9, 1.4, 14.0,))
labels = ['norm', 'index', 'cutoff']

# Initialize in different ways to test argument validation

@pytest.mark.skipif('not HAS_EMCEE')
def test_init():
    sampler, pos = get_sampler(
        data_table=data_table, p0=p0, labels=labels, model=cutoffexp,
        prior=lnprior, nwalkers=10, nburn=0, threads=1)

    sampler, pos = run_sampler(
        data_table=data_table, p0=p0, labels=labels, model=cutoffexp,
        prior=lnprior, nwalkers=10, nburn=2, nrun=2, threads=1)

    # test that the CL keyword has been correctly read
    assert sampler.data['cl'] == 0.99


@pytest.mark.skipif('not HAS_EMCEE')
def test_init_symmetric_dflux():
    # symmetric data_table errors
    sampler, pos = run_sampler(
        data_table=data_table2, p0=p0, labels=labels, model=cutoffexp,
        prior=lnprior, nwalkers=10, nburn=2, nrun=2, threads=1)

@pytest.mark.skipif('not HAS_EMCEE')
def test_init_labels():
    # labels
    sampler, pos = run_sampler(data_table=data_table, p0=p0, labels=None, model=cutoffexp,
                               prior=lnprior, nwalkers=10, nrun=2, nburn=0, threads=1)
    sampler, pos = run_sampler(
        data_table=data_table, p0=p0, labels=labels[:2], model=cutoffexp,
        prior=lnprior, nwalkers=10, nrun=2, nburn=0, threads=1)

@pytest.mark.skipif('not HAS_EMCEE')
def test_init_prior():
    # no prior
    sampler, pos = run_sampler(
        data_table=data_table, p0=p0, labels=labels, model=cutoffexp,
        prior=None, nwalkers=10, nrun=2, nburn=0, threads=1)

@pytest.mark.skipif('not HAS_EMCEE')
def test_init_exception_model():
    # test exception raised when no model or data_table are provided
    with pytest.raises(TypeError):
        sampler, pos = get_sampler(data_table=data_table, p0=p0, labels=labels,
                                   prior=lnprior, nwalkers=10, nburn=0, threads=1)

@pytest.mark.skipif('not HAS_EMCEE')
def test_init_exception_data():
    with pytest.raises(TypeError):
        sampler, pos = get_sampler(p0=p0, labels=labels, model=cutoffexp,
                                   prior=lnprior, nwalkers=10, nburn=0, threads=1)

@pytest.mark.skipif('not HAS_EMCEE')
def test_multiple_data_tables():
    sampler, pos = get_sampler(data_table=[data_table, data_table2], p0=p0,
            labels=labels, model=cutoffexp, prior=lnprior, nwalkers=10, nburn=0,
            threads=1)

@pytest.mark.skipif('not HAS_EMCEE')
def test_data_table_in_list():
    sampler, pos = get_sampler(data_table=[data_table], p0=p0,
            labels=labels, model=cutoffexp, prior=lnprior, nwalkers=10, nburn=0,
            threads=1)

