"""Contains functions for calculating relaxation times
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

from .omegaint import omega
from scipy import constants
from scipy.special import gamma
from . import crosssection as cs
from .particles import Particle, Molecule
import numpy as np


def rot_rel_time_vss(T: float, idata: np.ndarray, molecule: Molecule,
                     n: float,  model: str='VSS') -> float:
    """Calculates the rotational relaxation time using the VSS/VHS/rigid sphere models and Parker's formula

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule for which the rotational relaxation time is being calculated
    n : float
        the numeric density of the mixture
    model : str
        the interaction model to be used, possible values:
            * 'VSS' (Variable Soft Sphere model)
            * 'VHS' (Variable Hard Sphere model)
            * the rigid sphere model will be used otherwise

        defaults to `'VSS'`

    Returns
    -------
    float
        Rotational relaxation time
    """
    return raw_rot_rel_time_vss(T, idata[0], molecule.LJe, idata[9], idata[10], idata[11], idata[12],
                                molecule.mass, n, molecule.infcoll, model)


def rot_rel_time(T: float, idata: np.ndarray, molecule: Molecule, n: float,
                 model: str='ESA', Zr_model: str='VSS') -> float:
    """Calculates the rotational relaxation time using Parker's formula and the :math:`\\Omega^{(2,2)}` integral

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule for which the rotational relaxation time is being calculated
    n : float
        the numeric density of the mixture
    model : str
        the interaction model to be used to calculate the :math:`\\Omega^{(2,2)}` integral, possible values:
            * 'ESA' (model given in the paper *Transport Properties of High-Temperature Mars-Atmosphere Components*)
            * 'BM' (Inverse Power Law potential)
            * 'LJ' (Lennard-Jones potential)
            * 'MLJ' (Modified Lennard-Jones model)
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'Switch' (returns the result for the Lennard-Jones model when :math:`T / \\varepsilon_{cd} < 10`
              and for the IPL potential otherwise)

        defaults to 'ESA'
    Zr_model : str
        the model used to calculate the collision amount needed to reach rotational equilibrium, possible values:
            * 'VSS' (Variable Soft Sphere model)
            * 'VHS' (Variable Hard Sphere model)
            * the rigid sphere model will be used otherwise

        defaults to `'VSS'`

    Returns
    -------
    float
        Rotational relaxation time
    """
    return raw_rot_rel_time(omega(T, 2, 2, idata, model=model, nokt=False), n,
                            raw_Zr(T, idata[0], molecule.LJe, idata[10], idata[11], idata[12], molecule.mass,
                                   molecule.infcoll, Zr_model))


def rot_rel_time_def(T: float, idata: np.ndarray, molecule: Molecule, partner: Particle, n: float,
                     model: str='VSS', prob_model: str='EQ') -> float:
    """Calculates the rotational relaxation time using the definition (through the averaging of the squared
    rotational energy difference)

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule for which the rotational relaxation time is being calculated
    partner : Particle
        the collision partner
    n : float
        the numeric density of the mixture
    rig_sphere : bool, optional
        if ``True``, the rigid sphere model is used for the crosssection, if ``False``, the VSS is model is used,
        defaults to ``False``
    model : str, optional
        the elastic crosssection model to be used, possible values:

            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)

        defaults to 'VSS'
    prob_model : str, optional
        the model to be used for the probability of rotational transitions, possible value:

            * 'EQ' - all transitions are considered equiprobable

        defaults to 'EQ'

    Returns
    -------
    float
        Rotational relaxation time
    """
    if isinstance(partner, Molecule):
        if partner.name == molecule.name:
            return 0.25 / (n * cs.elastic_integral(T, 0, idata, model, False)
                           * (cs.dE_rot_sq(T, idata, molecule, False, model, prob_model)
                           + cs.dE_rot_c_dE_rot_d(T, idata, molecule, partner, False, model, prob_model)))
        else:
            return 0.25 / (n * cs.elastic_integral(T, 0, idata, model, False)
                           * (cs.dE_rot_dE_rot_full(T, idata, molecule, partner, False, model, prob_model)
                           + cs.dE_rot_dE_rot_full(T, idata, partner, molecule, False, model, prob_model)))

    else:
        return 0.25 / (n * cs.elastic_integral(T, 0, idata, model, False)
                       * cs.dE_rot_sq(T, idata, molecule, False, model, prob_model))


def Zr(T: float, idata: np.ndarray, molecule: Molecule, model: str='VSS') -> float:
    """Calculates the collision amount needed to reach rotational equilibrium using the VSS/VHS/rigid sphere models

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule for which the collision amount is being calculated
    infcoll : float
        the :math:`\\zeta_{\\inf}` parameter (Parker's limiting value)
    model : str
        the interaction model to be used, possible values:
            * 'VSS' (Variable Soft Sphere model)
            * 'VHS' (Variable Hard Sphere model)
            * the rigid sphere model will be used otherwise

        defaults to `'VSS'`

    Returns
    -------
    float
        Amount of collisions needed to reach rotational equilibrium
    """
    return raw_Zr(T, idata[0], molecule.LJe, idata[10], idata[11], idata[12], molecule.mass, molecule.infcoll, model)


def millikan_white(T: float, idata: np.ndarray, molecule: Molecule, p: float) -> float:
    """Calculates the VT relaxation time using the Millikan-White formula

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule for which the VT relaxation time is being calculated
    p : float
        the pressure (in atmospheres)

    Returns
    -------
    float
        VT relaxation time
    """
    return raw_millikan_white(T, idata[0], molecule.hvc, p)


def park_correction(T: float, molecule: Molecule, n: float):
    """Calculates the high-temperature correction to the VT relaxation time (Park's correction)

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule for which the VT relaxation time is being calculated
    n : float
        the numeric density of the mixture

    Returns
    -------
    float
        VT relaxation time correction
    """
    return raw_park_correction(T, molecule.mass, n)


def raw_rot_rel_time_vss(T: float, collision_mass: float, eps: float, vssc: float, vsso: float, vssc_deflection: float,
                         vsso_deflection: float, mass: float, n: float, infcoll: float, model: str='VSS') -> float:
    """Calculates the rotational relaxation time using the VSS/VHS/rigid sphere models and Parker's formula,
    *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    collision_mass : float
        the collision-reduced mass :math:`m_{cd}`
    eps : float
        the Lennard-Jones epsilon parameter :math:`\\varepsilon_{cd}`, divided by Boltzmann's constant
    vssc : float
        the :math:`C` parameter for the VSS model for the total cross-section
    vsso : float
        the :math:`\\omega` parameter for the VSS model for the total cross-section
    vssc_deflection : float
        the :math:`C` parameter for the VSS model for the deflection angle
    vsso_deflection : float
        the :math:`\\omega` parameter for the VSS model for the deflection angle
    mass : float
        the mass of the molecule for which the rotational relaxation time is being calculated
    n : float
        the numeric density of the mixture
    infcoll : float
        the :math:`\\zeta_{\\inf}` parameter (Parker's limiting value)
    model : str
        the interaction model to be used, possible values:
            * 'VSS' (Variable Soft Sphere model)
            * 'VHS' (Variable Hard Sphere model)
            * the Rigid Sphere model will be used otherwise

        defaults to `'VSS'`

    Returns
    -------
    float
        Rotational relaxation time
    """
    return raw_Zr(T, collision_mass, eps, vsso, vssc_deflection, vsso_deflection, mass,
                  infcoll, model) / ((vssc * n * ((8 * constants.k * T / (constants.pi * collision_mass)) ** 0.5)
                                      * (T ** -vsso) * gamma(2 - vsso))
                                     * (constants.physical_constants['Angstrom star'][0] ** 2))


def raw_rot_rel_time(omega_integral: float, n: float, Zr: float) -> float:
    """Calculates the rotational relaxation time using Parker's formula and the :math:`\\Omega^{(2,2)}` integral,
    *raw* version

    Parameters
    ----------
    omega_integral : float
        the value of the dimensional :math:`\\Omega^{(2,2)}` integral to be used in the calculation
    n : float
        the numeric density of the mixture
    Zr : float
        the amount of collisions required to reach rotational equilibrium

    Returns
    -------
    float
        Rotational relaxation time
    """
    return 0.15625 * constants.pi * Zr / (n * omega_integral)  # 0.15625 is 5 / 32


def raw_Zr(T: float, collision_mass: float, eps: float, vsso: float, vssc_deflection: float, vsso_deflection: float,
           mass: float, infcoll: float, model: str='VSS') -> float:
    """Calculates the collision amount needed to reach rotational equilibrium using the VSS/VHS/rigid sphere models,
    *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    collision_mass : float
        the collision-reduced mass :math:`m_{cd}`
    eps : float
        the Lennard-Jones :math:`\\varepsilon_{cd}` parameter of the molecule, divided by Boltzmann's constant
    vsso : float
        the :math:`\\omega` parameter for the VSS model for the total cross-section
    vssc_deflection : float
        the :math:`C` parameter for the VSS model for the deflection angle
    vsso_deflection : float
        the :math:`\\omega` parameter for the VSS model for the crosssection
    mass : float
        the mass of the molecule for which the rotational relaxation time is being calculated
    infcoll : float
        the :math:`\\zeta_{\\inf}` parameter (Parker's limiting value)
    model : str
        the interaction model to be used, possible values:
            * 'VSS' (Variable Soft Sphere model)
            * 'VHS' (Variable Hard Sphere model)
            * the Rigid Sphere model will be used otherwise

        defaults to `'VSS'`

    Returns
    -------
    float
        Amount of collisions needed to reach rotational equilibrium
    """
    if model == 'VSS':
        alpha = vssc_deflection * (T ** vsso_deflection)
        vssomega = vsso
    elif model == 'VHS':
        alpha = 1.0
        vssomega = vsso
    else:
        alpha = 1.0
        vssomega = 0.0

    TTstar = eps / T
    div = (2.0 - vssomega) / (1.0 + alpha) + 0.5 * (constants.pi ** 1.5) * gamma(1.0 + alpha) * gamma(2.5 - vssomega)\
        * (TTstar ** 0.5) / (gamma(1.5 + alpha) * gamma(2.0 - vssomega)) + (2.0 + 0.25 * (constants.pi ** 2)) * TTstar
    return mass * infcoll / (2.0 * div * collision_mass)


def raw_millikan_white(T: float, mass: float, molecule_hvc: float, p: float) -> float:
    """Calculates the VT relaxation time using the Millikan-White formula, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    molecule_hvc : float
        the harmonic coefficient in the formula for vibrational level energies
    p : float
        the pressure (in atmospheres)

    Returns
    -------
    float
        VT relaxation time
    """
    mu = mass * 1000.0 * constants.N_A
    return (10.0 ** (0.0005 * (mu ** 0.5) * ((molecule_hvc / constants.k) ** (4.0 / 3.0))
                     * (T ** (-1.0 / 3.0) - 0.015 * (mu ** 0.25)) - 8.0)) / p

#
# def raw_park_correction(T, mass, n):
#     mu = mass * 1000.0 * constants.N_A
#     return (10 ** 20) / (n * ((4 * constants.k * T / (constants.pi * mu)) ** 0.5))