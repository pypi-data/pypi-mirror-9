"""Contains functions for calculating VV- and VT- rates
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"


from .crosssection import vt_integral_fho, vv_integral_fho
from .particles import Molecule
from .probabilities import ssh_vt_p10
from scipy import constants
import numpy as np
from math import exp
from .errors import KineticlibError


def vt_rate_ssh(T: float, idata: np.ndarray, molecule: Molecule, i: int, delta: int) -> float:
    """Calculates the VT transition rate constant using the SSH model
    for the following process: **M(i) + P -> M(i + delta) + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which undergoes the VT transition
    i : int
        the vibrational level of the molecule
    delta : int
        the change in vibrational level of the molecule

    Returns
    -------
    float
        The VT transition rate

    Raises
    ------
    KineticlibError
        if ``delta`` is not equal to 1 or -1
    """
    if delta == -1:
        return raw_vt_rate_ssh_harmonic_down(T, idata[1], idata[0], idata[2], molecule.hvc, i)
    elif delta == 1:
        return raw_vt_rate_ssh_harmonic_up(T, idata[1], idata[0], idata[2], molecule.vibr[i],
                                           molecule.vibr[i+1], molecule.hvc, i)
    else:
        raise KineticlibError('Only one-quantum transition rates can be calculated using the SSH model')


def vt_rate_fho(T: float, idata: np.ndarray, molecule: Molecule, model: str='VSS') -> float:
    """Calculates the VT transition rate constant using the FHO probability and VSS or rigid sphere cross-section models
    for the following process: **M(i) + P -> M(i + delta) + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which undergoes the VT transition
    i : int
        the vibrational level of the molecule
    delta : int
        the change in vibrational level of the molecule
    model : str, optional
        the elastic crosssection model to be used, possible values:
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
    float
        The VT transition rate

    """
    return 8. * vt_integral_fho(T, 0, idata, molecule, i, delta, model, False)


def vv_rate_fho(T: float, idata: np.ndarray, molecule1: Molecule, molecule2: Molecule, i: int, k: int, i_delta: int,
                model: str='VSS') -> float:
    """Calculates the VV transition rate constant using the FHO probability and VSS or rigid sphere cross-section models
    for the following process: **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule1 : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule M1
    molecule2 : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule M2
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1
    model : str, optional
        the elastic crosssection model to be used, possible values:
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
    float
        The VV transition rate

    """
    return 8. * vv_integral_fho(T, 0, idata, molecule1, molecule2, i, k, i_delta, model, False)


def raw_vt_rate_ssh_harmonic_down(T: float, sigma: float, mass: float, eps: float, hvc: float, i: int) -> float:
    """Calculates the VT transition rate constant using the SSH model
    for the following process: **M(i) + P -> M(i - 1) + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    eps : float
        the Lennard-Jones :math:`\\varepsilon_{cd}` parameter, divided by Boltzmann's constant
    hvc : float
        the harmonic coefficient in the formula for vibrational level energies
    i : int
        the vibrational level of the molecule

    Returns
    -------
    float
        The VT transition rate

    """
    return i * 2. * sigma**2 * ((2 * constants.pi * constants.k * T / mass) ** 0.5) * ssh_vt_p10(T, mass, eps, hvc)


def raw_vt_rate_ssh_harmonic_up(T: float, sigma: float, mass: float, eps: float,
                                ve_before: float, ve_after: float, hvc: float, i: int) -> float:
    """Calculates the VT transition rate constant using the SSH model
    for the following process: **M(i) + P -> M(i + 1) + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    eps : float
        the Lennard-Jones :math:`\\varepsilon_{cd}` parameter, divided by Boltzmann's constant
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    hvc : float
        the harmonic coefficient in the formula for vibrational level energies
    i : int
        the vibrational level of the molecule

    Returns
    -------
    float
        The VT transition rate

    """
    return raw_vt_rate_ssh_harmonic_down(T, sigma, mass, eps, hvc, i) * exp((ve_before - ve_after) / (constants.k * T))