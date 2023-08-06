"""Contains various elastic and inelastic crosssections and generalized omega integrals
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"

import numpy as np
from scipy import constants
from scipy.misc import factorial
from scipy import integrate
from .particles import MoleculeMultiT, Molecule, MoleculeQuasi, MoleculeOneT
from . import probabilities as prob
from .errors import KineticlibError
from math import exp, gamma, erf


def crosssection_elastic(g: float, T: float, idata: np.ndarray, model: str='VSS') -> float:
    """
    Calculates the VSS or rigid sphere crosssection

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    model : str, optional
        the elastic crosssection model to be used, possible values:
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
        The VSS or rigid sphere crosssection
    """
    if model == 'GSS':
        return (constants.physical_constants['Angstrom star'][0] ** 2) * \
               raw_crosssection_elastic_gss(g, T, idata[16], idata[17], idata[18], idata[19])
    elif model == 'VSS':
        return (constants.physical_constants['Angstrom star'][0] ** 2) * \
               raw_crosssection_elastic_vss(g, T, idata[9], idata[10])
    else:
        return raw_crosssection_elastic_rigid_sphere(idata[1])


def elastic_collision_time(T: float, idata: np.ndarray, n: float):
    """
    Calculates the elastic collision time using the VSS crosssection

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    n : float
        the numeric density of the mixture

    Returns
    -------
        The elastic collision time
    """
    return raw_elastic_collision_time(T, idata[0], idata[9], idata[10], n)


def crosssection_vt_fho(g: float, T: float, idata: np.ndarray, molecule: Molecule, i: int, delta: int,
                        model: str='VSS') -> float:
    """Calculates the VT crosssection using the FHO probability and VSS or
    rigid sphere cross-section models for the following process: **M(i) + P -> M(i + delta) + P**

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which undergoes the VT transition
    i : int
        the vibrational level of the molecule undergoing the transition
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
        The VT crosssection

    Raises
    ------
    KineticlibError
        if ``delta == 0``
    """
    if delta != 0:
        if model == 'GSS':
            return (constants.physical_constants['Angstrom star'][0] ** 2) *\
                   raw_crosssection_vt_gss_fho(g, T, idata[0], idata[4], idata[16], idata[17], idata[18], idata[19],
                                               molecule.vibr[i], molecule.vibr[i + delta],
                                               molecule.diss, i, delta)
        elif model == 'VSS':
            return (constants.physical_constants['Angstrom star'][0] ** 2) *\
                   raw_crosssection_vt_vss_fho(g, T, idata[0], idata[4], idata[9], idata[10], molecule.vibr[i],
                                               molecule.vibr[i + delta], molecule.diss,
                                               i, delta)
        else:
            return raw_crosssection_vt_rigid_sphere_fho(g, T, idata[0], idata[0], idata[4], molecule.vibr[i],
                                                        molecule.vibr[i + delta], molecule.diss,
                                                        i, delta)
    else:
        raise KineticlibError('VT transition with no change in vibrational level specified')


def crosssection_vv_fho(g: float, T: float, idata: np.ndarray, molecule1: Molecule, molecule2: Molecule, i: int,
                        k: int, i_delta: int, model: str='VSS') -> float:
    """Calculates the VV crosssection using the FHO probability and VSS or
    rigid sphere cross-section models for the following process:
    **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
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
        The VV crosssection

    Raises
    ------
    KineticlibError
        if ``i_delta == 0``
    """
    if i_delta != 0:
        if model == 'GSS':
            return (constants.physical_constants['Angstrom star'][0] ** 2) *\
                   raw_crosssection_vv_gss_fho(g, T, idata[0], idata[4], idata[16], idata[17], idata[18], idata[19],
                                               molecule1.vibr[i], molecule1.vibr[i + i_delta],
                                               molecule2.vibr[k], molecule2.vibr[k - i_delta], i, k, i_delta)
        elif model == 'VSS':
            return (constants.physical_constants['Angstrom star'][0] ** 2) *\
                   raw_crosssection_vv_vss_fho(g, T, idata[0], idata[4], idata[9], idata[10],
                                               molecule1.vibr[i], molecule1.vibr[i + i_delta],
                                               molecule2.vibr[k], molecule2.vibr[k - i_delta], i, k, i_delta)
        else:
            return raw_crosssection_vv_rigid_sphere_fho(g, T, idata[1], idata[0], idata[4],
                                                        molecule1.vibr[i], molecule1.vibr[i + i_delta],
                                                        molecule2.vibr[k], molecule2.vibr[k - i_delta], i, k, i_delta)
    else:
        raise KineticlibError('VV transition with no change in vibrational level specified')


def crosssection_diss(g: float, T: float, idata: np.ndarray, molecule: Molecule, i: int,
                      center_of_mass: bool=True, vl_dependent: bool=True, model: str='VSS') -> float:
    """Calculates the dissociation crosssection either using the VSS or rigid sphere model for the process
    **AB(i) + P -> A + B + P**

    **Note** if integrating over the crosssection, the integration must be performed not from :math:`0` to
    :math:`\\infty`, but from :math:`g_{min}` to :math:`\\infty` (because the crosssection is discontinuous),
    where :math:`g_{min}` is the minimum value of the dimensionless velocity at which the crosssection is non-zero,
    it can be calculated using the ``min_dimensionless_vel_diss`` function

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule :  Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which dissociates
    i : int
        the vibrational level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    model : str, optional
        the elastic crosssection model to be used, possible values:
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
    float
        The dissociation crosssection
    """
    if isinstance(molecule, MoleculeMultiT):
        offset_energy = molecule.vibr[i] + molecule.vibr_zero
    else:
        offset_energy = molecule.vibr[i]
    if model == 'GSS':
        return (constants.physical_constants['Angstrom star'][0] ** 2) *\
               raw_crosssection_diss_gss(g, T, idata[16], idata[17], idata[18], idata[19], offset_energy,
                                         molecule.diss, center_of_mass, vl_dependent)
    elif model == 'VSS':
        return (constants.physical_constants['Angstrom star'][0] ** 2) *\
               raw_crosssection_diss_vss(g, T, idata[9], idata[10], offset_energy, molecule.diss, center_of_mass,
                                         vl_dependent)
    else:
        return raw_crosssection_diss_rigid_sphere(g, T, idata[1], offset_energy, molecule.diss, center_of_mass,
                                                  vl_dependent)


def min_dimensionless_vel_diss(T: float, molecule: Molecule, i: int, vl_dependent: bool=True) -> float:
    """Calculates the minimum value of the dimensionless relative velocity of colliding particles for which
    the dissociation crosssection is not zero for the process **AB(i) + P -> A + B + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which dissociates
    i : int
        the vibrational level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value)
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``

    Returns
    -------
    float
        The minimum value of the dimensionless relative velocity

    """
    if isinstance(molecule, MoleculeMultiT):
        return raw_min_dimensionless_vel_diss(T, molecule.vibr[i] + molecule.vibr_zero, molecule.diss,
                                              vl_dependent)
    else:
        return raw_min_dimensionless_vel_diss(T, molecule.vibr[i], molecule.diss, vl_dependent)


def vt_integral_fho(T: float, deg: int, idata: np.ndarray, molecule: Molecule, i: int, delta: int,
                    model: str='VSS', nokt: bool=False) -> float:
    """Calculates the generalized VT omega integral using the FHO probability and VSS or
    rigid sphere cross-section models for the following process: **M(i) + P -> M(i + delta) + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    idata : 1-D array-like
        the array of interaction data
    molecule :  Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which undergoes the VT transition
    i : int
        the vibrational level of the molecule undergoing the transition
    delta : int
        the change in vibrational level of the molecule
    model : str, optional
        the elastic crosssection model to be used, possible values
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the VT crosssection

    Raises
    ------
    KineticlibError
        if ``delta == 0``
    """
    if model == 'GSS':
        return raw_vt_integral_gss_fho(T, deg, idata[0], idata[4], idata[16], idata[17], idata[18], idata[19],
                                       molecule.vibr[i], molecule.vibr[i + delta], molecule.diss,
                                       i, delta, nokt)
    elif model == 'VSS':
        return raw_vt_integral_vss_fho(T, deg, idata[0], idata[4], idata[9], idata[10], molecule.vibr[i],
                                       molecule.vibr[i + delta], molecule.diss, i, delta, nokt)
    else:
        return raw_vt_integral_rigid_sphere_fho(T, deg, idata[1], idata[0], idata[4], molecule.vibr[i],
                                                molecule.vibr[i + delta], molecule.diss,
                                                i, delta, nokt)


def vv_integral_fho(T: float, deg: int, idata: np.ndarray, molecule1: Molecule, molecule2: Molecule, i: int,
                    k: int, i_delta: int, model: str='VSS', nokt=False) -> float:
    """Calculates the generalized VV omega integral using the FHO probability and VSS or
    rigid sphere cross-section models for the following process:
    **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    idata : 1-D array-like
        the array of interaction data
    molecule1 :  Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule M1
    molecule2 :  Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
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
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the VV crosssection

    Raises
    ------
    KineticlibError
        if ``i_delta == 0``
    """
    if model == 'GSS':
        return raw_vv_integral_gss_fho(T, deg, idata[0], idata[4], idata[16], idata[17], idata[18], idata[19],
                                       molecule1.vibr[i], molecule1.vibr[i + i_delta],
                                       molecule2.vibr[k], molecule2.vibr[k - i_delta], i, k, i_delta, nokt)
    elif model == 'VSS':
        return raw_vv_integral_vss_fho(T, deg, idata[0], idata[4], idata[9], idata[10],
                                       molecule1.vibr[i], molecule1.vibr[i + i_delta],
                                       molecule2.vibr[k], molecule2.vibr[k - i_delta], i, k, i_delta, nokt)
    else:
        return raw_vv_integral_vss_fho(T, deg, idata[0], idata[4], idata[9], idata[10],
                                       molecule1.vibr[i], molecule1.vibr[i + i_delta],
                                       molecule2.vibr[k], molecule2.vibr[k - i_delta], i, k, i_delta, nokt)


def diss_integral(T: float, deg: int, idata: np.ndarray, molecule: Molecule, i: int,
                  center_of_mass: bool=True, vl_dependent: bool=True, model: str='VSS', nokt: bool=False) -> float:
    """Calculates the generalized dissociation omega integral either using the VSS or rigid sphere model
    for the process **AB(i) + P -> A + B + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    idata : 1-D array-like
        the array of interaction data
    molecule :  Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which dissociates
    i : int
        the vibrational level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    model : str, optional
        the elastic crosssection model to be used, possible values:

            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the dissociation crosssection
    """
    if isinstance(molecule, MoleculeMultiT):
        offset_energy = molecule.vibr[i] + molecule.vibr_zero
    else:
        offset_energy = molecule.vibr[i]

    if model == 'GSS':
        return raw_diss_integral_gss(T, deg, idata[0], idata[16], idata[17], idata[18], idata[19], offset_energy,
                                     molecule.diss, center_of_mass, vl_dependent, nokt)
    elif model == 'VSS':
        return raw_diss_integral_vss(T, deg, idata[0], idata[9], idata[10], offset_energy,
                                     molecule.diss, center_of_mass, vl_dependent, nokt)
    else:
        return raw_diss_integral_rigid_sphere(T, deg, idata[1], idata[0], offset_energy,
                                              molecule.diss, center_of_mass, vl_dependent, nokt)


def elastic_integral(T: float, deg: int, idata: np.ndarray, model: str='VSS', nokt: bool=False) -> float:
    """Calculates the generalized elastic omega integral either using the VSS or rigid sphere model

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    idata : 1-D array-like
        the array of interaction data
    model : str, optional
        the elastic crosssection model to be used, possible values:
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the elastic crosssection
    """
    if model == 'GSS':
        return raw_elastic_integral_gss(T, deg, idata[0], idata[16], idata[17], idata[18], idata[19], nokt)
    elif model == 'VSS':
        return raw_elastic_integral_vss(T, deg, idata[0], idata[9], idata[10], nokt)
    else:
        return raw_elastic_integral_rigid_sphere(T, deg, idata[1], idata[0], nokt)


def vv_collisions_fho(T: float, T1_1: float, T1_2: float, idata: np.ndarray,
                      molecule1: MoleculeQuasi, molecule2: MoleculeQuasi,
                      model: str='VSS', nokt: bool=False) -> np.ndarray:
    """Calculates the averaging :math:`\\left<F \\right>^{VV}_{cd}` over all one-quantum VV crosssections of the type
    **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**,
    (with ``i_delta = 1`` and ``i_delta = -1``) of the following quantities:

        0. :math:`\\left(\\Delta\\mathcal{E}_{c} \\right)^2`
        #. :math:`\\left(\\Delta\\mathcal{E}_{d} \\right)^2`
        #. :math:`\\Delta\\mathcal{E}_{c}\\Delta\\mathcal{E}_{d}`
        #. :math:`\\Delta i \\Delta\\mathcal{E}_{c}`
        #. :math:`\\Delta i \\Delta\\mathcal{E}_{d}`
        #. :math:`\\Delta k \\Delta\\mathcal{E}_{c}`
        #. :math:`\\Delta k \\Delta\\mathcal{E}_{d}`
        #. :math:`\\Delta\\mathcal{E}_{c}`
        #. :math:`\\Delta\\mathcal{E}_{d}`
        #. :math:`\\left(\\Delta i \\right)^{2}`
        #. :math:`\\Delta i \\Delta k`
        #. :math:`\\Delta i`


    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1_1 : float
        the temperature of the first vibrational level of the molecule M1 (if the one-temperature approximation
        is used, can be set to any value)
    T1_2 : float
        the temperature of the first vibrational level of the molecule M2 (if the one-temperature approximation
        is used, can be set to any value)
    idata : 1-D array-like
        the array of interaction data
    molecule1 : MoleculeMultiT or MoleculeOneT
        the molecule M1
    molecule2 : MoleculeMultiT or MoleculeOneT
        the molecule M2
    model : str, optional
        the elastic crosssection model to be used, possible values:

            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    np.ndarray
        An array containing the averaged quantities listed above (in the same order)

    Raises
    KineticlibError
        If ``molecule1`` and  ``molecule2`` are of different types
    
    """
    result = np.zeros(12)
    if isinstance(molecule1, MoleculeMultiT) and isinstance(molecule2, MoleculeMultiT):
        a = np.arange(0, molecule1.num_vibr_levels(T, T1_1, True) + 1)
        b = np.arange(0, molecule2.num_vibr_levels(T, T1_2, True) + 1)
        vibr_exp1 = molecule1.vibr_exp(T, T1_1, a)
        vibr_exp2 = molecule2.vibr_exp(T, T1_2, b)
        molecule_num_vibr1 = molecule1.num_vibr_levels(T, T1_1)
        molecule_num_vibr2 = molecule2.num_vibr_levels(T, T1_2)
        Z_vibr1 = molecule1.Z_vibr(T, T1_1)
        Z_vibr2 = molecule1.Z_vibr(T, T1_2)

    elif isinstance(molecule1, MoleculeOneT) and isinstance(molecule2, MoleculeOneT):
        a = np.arange(0, molecule1.num_vibr + 1)
        b = np.arange(0, molecule2.num_vibr + 1)
        vibr_exp1 = molecule1.vibr_exp(T, a)
        vibr_exp2 = molecule2.vibr_exp(T, b)
        molecule_num_vibr1 = molecule1.num_vibr
        molecule_num_vibr2 = molecule2.num_vibr
        Z_vibr1 = molecule1.Z_vibr(T)
        Z_vibr2 = molecule1.Z_vibr(T)
    else:
        raise KineticlibError('Types of molecule1 and molecule2 do not match!')

    for k in range(molecule_num_vibr2):
        for i in range(molecule_num_vibr1):
            cs = vv_integral_fho(T, 0, idata, molecule1, molecule2, i, k + 1, 1, model, nokt)
            result[0] += ((molecule1.vibr[i] -
                           molecule1.vibr[i + 1]) ** 2) * vibr_exp1[i]\
                                                              * vibr_exp2[k + 1] * cs
            result[1] += ((molecule2.vibr[k + 1] -
                           molecule2.vibr[k]) ** 2) * vibr_exp1[i] \
                                                          * vibr_exp2[k + 1] * cs
            result[2] += ((molecule1.vibr[i + 1] - molecule1.vibr[i])
                          * (molecule2.vibr[k] - molecule2.vibr[k + 1])) * vibr_exp1[i]\
                                                                                     * vibr_exp2[k + 1]\
                                                                                     * cs
            result[3] += (molecule1.vibr[i + 1] - molecule1.vibr[i]) * vibr_exp1[i]\
                                                                                 * vibr_exp2[k + 1] * cs
            result[4] += (molecule2.vibr[k] -
                          molecule2.vibr[k + 1]) * vibr_exp1[i] \
                                                       * vibr_exp2[k + 1] * cs
            result[5] -= (molecule1.vibr[i + 1] -
                          molecule1.vibr[i]) * vibr_exp1[i] \
                                                   * vibr_exp2[k + 1] * cs
            result[6] -= (molecule2.vibr[k] -
                          molecule2.vibr[k + 1]) * vibr_exp1[i] \
                                                       * vibr_exp2[k + 1] * cs
            result[7] += (molecule1.vibr[i + 1] -
                          molecule1.vibr[i]) * vibr_exp1[i] \
                                                       * vibr_exp2[k + 1] * cs
            result[8] += (molecule2.vibr[k] -
                          molecule2.vibr[k + 1]) * vibr_exp1[i] \
                                                       * vibr_exp2[k + 1] * cs
            result[9] += vibr_exp1[i] * vibr_exp2[k + 1] * cs
            result[10] -= vibr_exp1[i] * vibr_exp2[k + 1] * cs
            result[11] += vibr_exp1[i] * vibr_exp2[k + 1] * cs

            cs = vv_integral_fho(T, 0, idata, molecule1, molecule2, i + 1, k, -1, model, nokt)
            result[0] += ((molecule1.vibr[i] - molecule1.vibr[i + 1]) ** 2)\
                * vibr_exp1[i + 1] * vibr_exp2[k] * cs
            result[1] += ((molecule2.vibr[k] - molecule2.vibr[k + 1]) ** 2)\
                * vibr_exp1[i + 1] * vibr_exp2[k] * cs
            result[2] += ((molecule1.vibr[i] - molecule1.vibr[i + 1])
                          * (molecule2.vibr[k + 1] -
                             molecule2.vibr[k]))\
                          * vibr_exp1[i + 1] * vibr_exp2[k] * cs
            result[3] -= (molecule1.vibr[i] -
                          molecule1.vibr[i + 1]) * vibr_exp1[i + 1] \
                                                       * vibr_exp2[k] * cs
            result[4] -= (molecule2.vibr[k + 1] -
                          molecule2.vibr[k]) * vibr_exp1[i + 1] \
                                                   * vibr_exp2[k] * cs
            result[5] += (molecule1.vibr[i] -
                          molecule1.vibr[i + 1]) * vibr_exp1[i + 1] \
                                                       * vibr_exp2[k] * cs
            result[6] += (molecule2.vibr[k + 1] -
                          molecule2.vibr[k]) * vibr_exp1[i + 1] \
                                                   * vibr_exp2[k] * cs
            result[7] += (molecule1.vibr[i] -
                          molecule1.vibr[i + 1]) * vibr_exp1[i + 1] \
                                                       * vibr_exp2[k] * cs
            result[8] += (molecule2.vibr[k + 1] -
                          molecule2.vibr[k]) * vibr_exp1[i + 1] \
                                                   * vibr_exp2[k] * cs
            result[9] += vibr_exp1[i + 1] * vibr_exp2[k] * cs
            result[10] -= vibr_exp1[i + 1] * vibr_exp2[k] * cs
            result[11] -= vibr_exp1[i + 1] * vibr_exp2[k] * cs
    result[0:3] /= (constants.k * T) ** 2
    result[3:9] /= constants.k * T
    return result / (Z_vibr1 * Z_vibr2)


def dE_rot_sq(T: float, idata: np.ndarray, molecule: Molecule, full_integral: bool=True,
              model: str='VSS', prob_model: str='EQ', nokt: bool=False) -> float:
    """Calculates either the partial averaging of the squared change in rotational energy
    over all one-quantum rotational transitions
    :math:`\\left<\\left(\\Delta \\mathcal{E}^{rot}_{c}\\right)^{2}\\right>_{part}`
    or the full averaging of the same quantity :math:`\\left<\\left(\\Delta \\mathcal{E}^{rot}_{c}\\right)^{2}\\right>`,
    considering all one-quantum transitions to be equiprobable

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which undergoes the rotational energy transition
    full_integral : bool
        if ``True``, the full averaging is calculated, if ``False``,
        the partial averaging is calculated, defaults to ``True`` (this parameter plays a role only when
        ``prob_model`` is set to ``EQ``)
    model : str, optional
        the elastic crosssection model to be used, possible values:

            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'
    prob_model : str, optional
        the model to be used for the probability of rotational transitions, possible value:

            * 'EQ' - all transitions are considered equiprobable

        defaults to 'EQ'
    nokt : bool, optional
        if ``True`` and ``full_integral`` is ``True``, the result will be multiplied
        by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The calculated averaging
    """
    if full_integral:
        return raw_dE_rot_sq_equiprob(T, molecule.Z_rot(T), molecule.rot_symmetry,
                                      molecule.rot_const, molecule.num_rot) * elastic_integral(T, 0, idata, model, nokt)
    else:
        return raw_dE_rot_sq_equiprob(T, molecule.Z_rot(T), molecule.rot_symmetry,
                                      molecule.rot_const, molecule.num_rot)


def dE_rot_single(T: float, idata: np.ndarray, molecule: Molecule, full_integral: bool=True,
                  model: str='VSS', prob_model: str='EQ', nokt: bool=False) -> float:
    """Calculates either the partial averaging of the change in rotational energy
    over all one-quantum rotational transitions
    :math:`\\left<\\Delta \\mathcal{E}^{rot}_{c}\\right>_{part}`
    or the full averaging of the same quantity :math:`\\left<\\Delta \\mathcal{E}^{rot}_{c}\\right>`,
    considering all one-quantum transitions to be equiprobable

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which undergoes the rotational energy transition
    full_integral : bool
        if ``True``, the full averaging is calculated, if ``False``,
        the partial averaging is calculated, defaults to ``True`` (this parameter plays a role only when
        ``prob_model`` is set to ``EQ``)
    model : str, optional
        the elastic crosssection model to be used, possible values:

            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'
    prob_model : str, optional
        the model to be used for the probability of rotational transitions, possible value:

            * 'EQ' - all transitions are considered equiprobable

        defaults to 'EQ'
    nokt : bool, optional
        if ``True`` and ``full_integral`` is ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`,
        defaults to ``False``

    Returns
    -------
    float
        The calculated averaging
    """
    if full_integral:
        return raw_dE_rot_single_equiprob(T, molecule.Z_rot(T), molecule.rot_symmetry, molecule.rot_const,
                                          molecule.num_rot) * elastic_integral(T, 0, idata, model, nokt)
    else:
        return raw_dE_rot_single_equiprob(T, molecule.Z_rot(T), molecule.rot_symmetry, molecule.rot_const,
                                   molecule.num_rot)


def dE_rot_c_dE_rot_d(T: float, idata: np.ndarray, molecule1: Molecule, molecule2: Molecule,
                      full_integral: bool=True, model: str='VSS', prob_model: str='EQ', nokt: bool=False) -> float:
    """Calculates either the partial averaging of the product of changes in rotational energy of two molecules
    over all one-quantum rotational transitions
    :math:`\\left<\\Delta \\mathcal{E}^{rot}_{c}\\Delta \\mathcal{E}^{rot}_{d}\\right>_{part}`
    or the full averaging of the same quantity
    :math:`\\left<\\Delta \\mathcal{E}^{rot}_{c}\\Delta \\mathcal{E}^{rot}_{d}\\right>`,
    considering all one-quantum transitions to be equiprobable

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule1 : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the first molecule which undergoes the rotational energy transition
    molecule2 : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the second molecule which undergoes the rotational energy transition
    full_integral : bool
        if ``True``, the full averaging is calculated, if ``False``,
        the partial averaging is calculated, defaults to ``True`` (this parameter plays a role only when
        ``prob_model`` is set to ``EQ``)
    model : str, optional
        the elastic crosssection model to be used, possible values:
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)

        defaults to 'VSS'
    prob_model : str, optional
        the model to be used for the probability of rotational transitions, possible value:

            * 'EQ' - all transitions are considered equiprobable

        defaults to 'EQ'
    nokt : bool, optional
        if ``True`` and ``full_integral`` is ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`,
        defaults to ``False``

    Returns
    -------
    float
        The calculated averaging
    """
    if full_integral:
        return raw_dE_rot_single_equiprob(T, molecule1.Z_rot(T), molecule1.rot_symmetry, molecule1.rot_const,
                                          molecule1.num_rot)\
               * raw_dE_rot_single_equiprob(T, molecule2.Z_rot(T), molecule2.rot_symmetry, molecule2.rot_const,
                                            molecule2.num_rot) * elastic_integral(T, 0, idata, model, nokt)
    else:
        return raw_dE_rot_single_equiprob(T, molecule1.Z_rot(T), molecule1.rot_symmetry, molecule1.rot_const,
                                          molecule1.num_rot)\
               * raw_dE_rot_single_equiprob(T, molecule2.Z_rot(T), molecule2.rot_symmetry, molecule2.rot_const,
                                            molecule2.num_rot)


def dE_rot_dE_rot_full(T: float, idata: np.ndarray, molecule1: Molecule, molecule2: Molecule,
                       full_integral: bool=True, model: str='VSS', prob_model: str='EQ', nokt: bool=False) -> float:
    """Calculates either the partial averaging of the product of changes in rotational energy of one molecule
    and both molecules over all one-quantum rotational transitions
    :math:`\\left<\\Delta \\mathcal{E}^{rot}_{c}\\left(\\Delta \\mathcal{E}^{rot}_{c}
    + \\Delta \\mathcal{E}^{rot}_{d} \\right)\\right>_{part}`
    or the full averaging of the same quantity
    :math:`\\left<\\Delta \\mathcal{E}^{rot}_{c}\\left(\\Delta \\mathcal{E}^{rot}_{c}
    + \\Delta \\mathcal{E}^{rot}_{d} \\right)\\right>`,
    considering all one-quantum transitions to be equiprobable

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule1 : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the first molecule which undergoes the rotational energy transition
    molecule2 : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the second molecule which undergoes the rotational energy transition
    full_integral : bool
        if ``True``, the full averaging is calculated, if ``False``,
        the partial averaging is calculated, defaults to ``True`` (this parameter plays a role only when
        ``prob_model`` is set to ``EQ``)
    model : str, optional
        the elastic crosssection model to be used, possible values:

            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)

        defaults to 'VSS'
    prob_model : str, optional
        the model to be used for the probability of rotational transitions, possible value:

            * 'EQ' - all transitions are considered equiprobable

        defaults to 'EQ'
    nokt : bool, optional
        if ``True`` and ``full_integral`` is ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`,
        defaults to ``False``

    Returns
    -------
    float
        The calculated averaging
    """
    if full_integral:
        return (raw_dE_rot_sq_equiprob(T, molecule1.Z_rot(T), molecule1.rot_symmetry, molecule1.rot_const,
                                       molecule1.num_rot)
                + raw_dE_rot_single_equiprob(T, molecule1.Z_rot(T),
                                             molecule1.rot_symmetry, molecule1.rot_const, molecule1.num_rot)
                * raw_dE_rot_single_equiprob(T, molecule2.Z_rot(T),
                                             molecule2.rot_symmetry, molecule2.rot_const, molecule2.num_rot))\
               * elastic_integral(T, 0, idata, model, nokt)
    else:
        return (raw_dE_rot_sq_equiprob(T, molecule1.Z_rot(T), molecule1.rot_symmetry, molecule1.rot_const,
                                       molecule1.num_rot)
                + raw_dE_rot_single_equiprob(T, molecule1.Z_rot(T),
                                             molecule1.rot_symmetry, molecule1.rot_const, molecule1.num_rot)
                * raw_dE_rot_single_equiprob(T, molecule2.Z_rot(T),
                                             molecule2.rot_symmetry, molecule2.rot_const, molecule2.num_rot))


def raw_crosssection_elastic_gss(g: float, T: float, gssc1: float, gssc2: float, gsso1: float, gsso2: float) -> float:
    """Calculates the GSS crosssection (in square Angstroms), *raw* version

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    gssc1 : float
        the elastic crosssection GSS potential :math:`C_{1}` parameter
    gssc2 : float
        the elastic crosssection GSS potential :math:`C_{2}` parameter
    gsso1 : float
        the elastic crosssection GSS potential :math:`\\omega_{1}` parameter
    gsso2 : float
        the elastic crosssection GSS potential :math:`\\omega_{2}` parameter

    Returns
    -------
        The VSS crosssection
    """
    return gssc1 * ((constants.k * T * (g ** 2)) ** gsso1) +\
           gssc2 * ((constants.k * T * (g ** 2)) ** gsso2)


def raw_crosssection_elastic_vss(g: float, T: float, vssc: float, vsso: float) -> float:
    """Calculates the VSS crosssection (in square Angstroms), *raw* version

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter

    Returns
    -------
        The VSS crosssection
    """
    return vssc * (T ** (-vsso)) * (g ** (-2 * vsso))


def raw_crosssection_elastic_rigid_sphere(sigma: float) -> float:
    """Calculates the rigid sphere crosssection, *raw* version

    Parameters
    ----------
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`

    Returns
    -------
    float
        The rigid sphere crosssection
    """
    return constants.pi * (sigma ** 2)


def raw_elastic_collision_time(T: float, mass: float, vssc: float, vsso: float, n: float):
    """
    Calculates the elastic collision time using the VSS crosssection, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter
    n : float
        the numeric density of the mixture

    Returns
    -------
        The elastic collision time
    """
    return 1.0 / (vssc * n * ((8 * constants.k * T / (constants.pi * mass)) ** 0.5) * (T ** -vsso) * gamma(2 - vsso)
                       * (constants.physical_constants['Angstrom star'][0] ** 2))


def raw_crosssection_vt_gss_fho(g: float, T: float, mass: float, beta: float, gssc1: float, gssc2: float,
                                gsso1: float, gsso2: float,
                                ve_before: float, ve_after: float, molecule_diss: float,
                                i: int, delta: int) -> float:
    """Calculates the VT crosssection (in square Angstroms) using the FHO probability and GSS model
    for the following process: **M(i) + P -> M(i + delta) + P**, *raw* version

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    gssc1 : float
        the elastic crosssection GSS potential :math:`C_{1}` parameter
    gssc2 : float
        the elastic crosssection GSS potential :math:`C_{2}` parameter
    gsso1 : float
        the elastic crosssection GSS potential :math:`\\omega_{1}` parameter
    gsso2 : float
        the elastic crosssection GSS potential :math:`\\omega_{2}` parameter
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    molecule_diss : float
        the dissociation energy of the molecule which undergoes the transition (with no offset)
    i : int
        the vibrational level of the molecule
    delta : int
        the change in the vibrational level of the molecule

    Returns
    -------
    float
        The VT crosssection
    """
    return prob.vt_probability_fho(g, T, mass, beta, ve_before, ve_after, molecule_diss, i, delta)\
           * raw_crosssection_elastic_gss(g, T, gssc1, gssc2, gsso1, gsso2)


def raw_crosssection_vt_vss_fho(g: float, T: float, mass: float, beta: float, vssc: float, vsso: float,
                                ve_before: float, ve_after: float, molecule_diss: float,
                                i: int, delta: int) -> float:
    """Calculates the VT crosssection (in square Angstroms) using the FHO probability and VSS model
    for the following process: **M(i) + P -> M(i + delta) + P**, *raw* version

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    molecule_diss : float
        the dissociation energy of the molecule which undergoes the transition (with no offset)
    i : int
        the vibrational level of the molecule
    delta : int
        the change in the vibrational level of the molecule

    Returns
    -------
    float
        The VT crosssection
    """
    return prob.vt_probability_fho(g, T, mass, beta, ve_before, ve_after, molecule_diss, i, delta)\
           * raw_crosssection_elastic_vss(g, T, vssc, vsso)


def raw_crosssection_vt_rigid_sphere_fho(g: float, T: float, sigma: float, mass: float, beta: float,
                                         ve_before: float, ve_after: float,
                                         molecule_diss: float, i: int, delta: int) -> float:
    """Calculates the VT crosssection using the FHO probability and rigid sphere model
    for the following process: **M(i) + P -> M(i + delta) + P**, *raw* version

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    molecule_diss : float
        the dissociation energy of the molecule which undergoes the transition (with no offset)
    i : int
        the vibrational level of the molecule
    delta : int
        the change in the vibrational level of the molecule

    Returns
    -------
    float
        The VT crosssection
    """
    return prob.vt_probability_fho(g, T, mass, beta, ve_before, ve_after, molecule_diss, i, delta)\
           * raw_crosssection_elastic_rigid_sphere(sigma)


def raw_crosssection_vv_gss_fho(g, T: float, mass: float, beta: float, gssc1: float, gssc2: float,
                                gsso1: float, gsso2: float,
                                ve_before1: float, ve_after1: float, ve_before2: float, ve_after2: float, i: int, k: int,
                                i_delta: int) -> float:
    """Calculates the VV crosssection (in square Angstroms) using the FHO probability and GSS model
    for the following process: **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**, *raw* version

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    gssc1 : float
        the elastic crosssection GSS potential :math:`C_{1}` parameter
    gssc2 : float
        the elastic crosssection GSS potential :math:`C_{2}` parameter
    gsso1 : float
        the elastic crosssection GSS potential :math:`\\omega_{1}` parameter
    gsso2 : float
        the elastic crosssection GSS potential :math:`\\omega_{2}` parameter
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1

    Returns
    -------
    float
        The VV crosssection
    """
    return prob.vv_probability_fho(g, T, mass, beta, ve_before1, ve_after1, ve_before2, ve_after2, i, k, i_delta)\
           * raw_crosssection_elastic_gss(g, T, gssc1, gssc2, gsso1, gsso2)


def raw_crosssection_vv_vss_fho(g, T: float, mass: float, beta: float, vssc: float, vsso: float,
                                ve_before1: float, ve_after1: float, ve_before2: float, ve_after2: float, i: int, k: int,
                                i_delta: int) -> float:
    """Calculates the VV crosssection (in square Angstroms) using the FHO probability and VSS model
    for the following process: **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**, *raw* version

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1

    Returns
    -------
    float
        The VV crosssection
    """
    return prob.vv_probability_fho(g, T, mass, beta, ve_before1, ve_after1, ve_before2, ve_after2, i, k, i_delta)\
           * raw_crosssection_elastic_vss(g, T, vssc, vsso)


def raw_crosssection_vv_rigid_sphere_fho(g, T: float, sigma: float, mass: float, beta: float,
                                         ve_before1: float, ve_after1: float, ve_before2: float, ve_after2: float,
                                         i: int, k: int, i_delta: int) -> float:
    """Calculates the VV crosssection using the FHO probability and rigid sphere model
    for the following process: **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**, *raw* version

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1

    Returns
    -------
    float
        The VV crosssection
    """
    return prob.vv_probability_fho(g, T, mass, beta, ve_before1, ve_after1, ve_before2, ve_after2, i, k, i_delta)\
           * raw_crosssection_elastic_rigid_sphere(sigma)


def raw_crosssection_diss_gss(g: float, T: float, gssc1: float, gssc2: float,
                              gsso1: float, gsso2: float, molecule_vibr: float,
                              molecule_diss: float, center_of_mass: bool=True,
                              vl_dependent: bool=True) -> float:
    """Calculates the dissociation crosssection (in square Angstroms) using the GSS model for the process
    **AB(i) + P -> A + B + P**, *raw* version

    **Note** if integrating over the crosssection, the integration must be performed not from :math:`0` to
    :math:`\\infty`, but from :math:`g_{min}` to :math:`\\infty` (because the crosssection is discontinuous),
    where :math:`g_{min}` is the minimum value of the dimensionless velocity at which the crosssection is non-zero,
    it can be calculated using the ``min_dimensionless_vel_diss`` function

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    gssc1 : float
        the elastic crosssection GSS potential :math:`C_{1}` parameter
    gssc2 : float
        the elastic crosssection GSS potential :math:`C_{2}` parameter
    gsso1 : float
        the elastic crosssection GSS potential :math:`\\omega_{1}` parameter
    gsso2 : float
        the elastic crosssection GSS potential :math:`\\omega_{2}` parameter
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value) (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``

    Returns
    -------
    float
        The dissociation crosssection
    """
    if vl_dependent:
        min_sq = molecule_vibr + constants.k * T * (g ** 2)
    else:
        min_sq = constants.k * T * (g ** 2)

    if min_sq < molecule_diss:
        return 0.0
    else:
        if center_of_mass:
            return raw_crosssection_elastic_gss(g, T, gssc1, gssc2, gsso1, gsso2) * (1.0 - molecule_diss / min_sq)
        else:
            return raw_crosssection_elastic_gss(g, T, gssc1, gssc2, gsso1, gsso2)


def raw_crosssection_diss_vss(g: float, T: float, vssc: float, vsso: float, molecule_vibr: float,
                              molecule_diss: float, center_of_mass: bool=True,
                              vl_dependent: bool=True) -> float:
    """Calculates the dissociation crosssection (in square Angstroms) using the VSS model for the process
    **AB(i) + P -> A + B + P**, *raw* version

    **Note** if integrating over the crosssection, the integration must be performed not from :math:`0` to
    :math:`\\infty`, but from :math:`g_{min}` to :math:`\\infty` (because the crosssection is discontinuous),
    where :math:`g_{min}` is the minimum value of the dimensionless velocity at which the crosssection is non-zero,
    it can be calculated using the ``min_dimensionless_vel_diss`` function

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value) (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``

    Returns
    -------
    float
        The dissociation crosssection
    """
    if vl_dependent:
        min_sq = molecule_vibr + constants.k * T * (g ** 2)
    else:
        min_sq = constants.k * T * (g ** 2)

    if min_sq < molecule_diss:
        return 0.0
    else:
        if center_of_mass:
            return raw_crosssection_elastic_vss(g, T, vssc, vsso) * (1.0 - molecule_diss / min_sq)
        else:
            return raw_crosssection_elastic_vss(g, T, vssc, vsso)


def raw_crosssection_diss_rigid_sphere(g: float, T: float, sigma: float, molecule_vibr: float,
                                       molecule_diss: float, center_of_mass: bool=True,
                                       vl_dependent: bool=True) -> float:
    """Calculates the dissociation crosssection either using the rigid sphere model for the process
    **AB(i) + P -> A + B + P**, *raw* version

    **Note** if integrating over the crosssection, the integration must be performed not from :math:`0` to
    :math:`\\infty`, but from :math:`g_{min}` to :math:`\\infty` (because the crosssection is discontinuous),
    where :math:`g_{min}` is the minimum value of the dimensionless velocity at which the crosssection is non-zero,
    it can be calculated using the ``min_dimensionless_vel_diss`` function

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    T : float
        the temperature of the mixture
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value) (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``

    Returns
    -------
    float
        The dissociation crosssection
    """
    if vl_dependent:
        min_sq = molecule_vibr + constants.k * T * (g ** 2)
    else:
        min_sq = constants.k * T * (g ** 2)

    if min_sq < molecule_diss:
        return 0.0
    else:
        if center_of_mass:
            return constants.pi * (sigma ** 2) * (1.0 - molecule_diss / min_sq)
        else:
            return constants.pi * (sigma ** 2)


def raw_min_dimensionless_vel_diss(T: float, molecule_vibr: float, molecule_diss: float,
                                   vl_dependent: bool=True) -> float:
    """Calculates the minimum value of the dimensionless relative velocity of colliding particles for which
    the dissociation crosssection is not zero for the process **AB(i) + P -> A + B + P**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value) (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``

    Returns
    -------
    float
        The minimum value of the dimensionless relative velocity

    """
    if vl_dependent:
        return ((molecule_diss - molecule_vibr) / (constants.k * T)) ** 0.5
    else:
        return (molecule_diss / (constants.k * T)) ** 0.5


def elastic_omega_g_only_vss(g: float, deg: int, vsso: float) -> float:
    """Calculates the velocity-dependent part of the integrand of the
    generalized elastic omega integral for the VSS model

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    deg : int
        the degree of the omega integral
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter

    Returns
    -------
    float
        The velocity-dependent part of the integrand of the generalized omega integral
    """
    return exp(-(g ** 2)) * (g ** (3 + 2 * (deg - vsso)))


def elastic_omega_g_only_rigid_sphere(g: float, deg: int) -> float:
    """Calculates the velocity-dependent part of the integrand of the
    generalized elastic omega integral for the rigid sphere model

    Parameters
    ----------
    g : float
        the dimensionless relative velocity of the particles
    deg : int
        the degree of the omega integral

    Returns
    -------
    float
        The velocity-dependent part of the integrand of the generalized omega integral
    """
    return exp(-(g ** 2)) * (g ** (3 + 2 * deg))


def raw_vt_integral_gss_fho(T: float, deg: int, mass: float, beta: float, gssc1: float, gssc2: float,
                            gsso1: float, gsso2: float, ve_before: float, ve_after: float,
                            molecule_diss: float, i: int,
                            delta: int, nokt: bool=False) -> float:
    """Calculates the generalized VT omega integral using the FHO probability and GSS
    cross-section model for the following process: **M(i) + P -> M(i + delta) + P**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    gssc1 : float
        the elastic crosssection GSS potential :math:`C_{1}` parameter
    gssc2 : float
        the elastic crosssection GSS potential :math:`C_{2}` parameter
    gsso1 : float
        the elastic crosssection GSS potential :math:`\\omega_{1}` parameter
    gsso2 : float
        the elastic crosssection GSS potential :math:`\\omega_{2}` parameter
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    molecule_diss : float
        the dissociation energy of the molecule which undergoes the transition (with no offset)
    i : int
        the vibrational level of the molecule
    delta : int
        the change in the vibrational level of the molecule
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the VT crosssection

    Raises
    ------
    KineticlibError
        if ``delta == 0``

    """
    if delta != 0:
        if delta == 1:
            mult = (i + 1)
        elif delta == -1:
            mult = i
        elif delta > 0:
            mult = prob.fact_div_fact(i, i + delta) / (factorial(delta) ** 2)
        else:
            mult = prob.fact_div_fact(i + delta, i) / (factorial(-delta) ** 2)

        if not nokt:
            mult *= (constants.physical_constants['Angstrom star'][0] ** 2)\
                    * ((T * constants.k / (2.0 * constants.pi * mass)) ** 0.5)
        else:
            mult *= (constants.physical_constants['Angstrom star'][0] ** 2)\
                    * ((0.5 / (constants.pi * mass)) ** 0.5)
        svt = prob.svt(delta)
        f1 = lambda g: prob.vt_prob_g_only_fho(g, T, mass, beta, ve_before, ve_after,
                                               i, delta, molecule_diss, svt)\
                    * elastic_omega_g_only_vss(g, deg, -gsso1)
        f2 = lambda g: prob.vt_prob_g_only_fho(g, T, mass, beta, ve_before, ve_after,
                                               i, delta, molecule_diss, svt)\
                    * elastic_omega_g_only_vss(g, deg, -gsso2)
        return mult * (gssc1 * ((constants.k * T) ** gsso1) * integrate.quad(f1, 0, np.inf)[0] +
                       gssc2 * ((constants.k * T) ** gsso2) * integrate.quad(f2, 0, np.inf)[0])
    else:
        raise KineticlibError('VT transition with no change in vibrational level specified')


def raw_vt_integral_vss_fho(T: float, deg: int, mass: float, beta: float, vssc: float, vsso: float,
                            ve_before: float, ve_after: float, molecule_diss: float, i: int,
                            delta: int, nokt: bool=False) -> float:
    """Calculates the generalized VT omega integral using the FHO probability and VSS
    cross-section model for the following process: **M(i) + P -> M(i + delta) + P**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    molecule_diss : float
        the dissociation energy of the molecule which undergoes the transition (with no offset)
    i : int
        the vibrational level of the molecule
    delta : int
        the change in the vibrational level of the molecule
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the VT crosssection

    Raises
    ------
    KineticlibError
        if ``delta == 0``

    """
    if delta != 0:
        if delta == 1:
            mult = (i + 1)
        elif delta == -1:
            mult = i
        elif delta > 0:
            mult = prob.fact_div_fact(i, i + delta) / (factorial(delta) ** 2)
        else:
            mult = prob.fact_div_fact(i + delta, i) / (factorial(-delta) ** 2)

        if not nokt:
            mult *= (constants.physical_constants['Angstrom star'][0] ** 2)\
                    * ((T * constants.k / (2.0 * constants.pi * mass)) ** 0.5)
        else:
            mult *= (constants.physical_constants['Angstrom star'][0] ** 2)\
                    * ((0.5 / (constants.pi * mass)) ** 0.5)

        svt = prob.svt(delta)
        f = lambda g: prob.vt_prob_g_only_fho(g, T, mass, beta, ve_before, ve_after,
                                              i, delta, molecule_diss, svt)\
                    * elastic_omega_g_only_vss(g, deg, vsso)
        return mult * vssc * (T ** (-vsso)) * integrate.quad(f, 0, np.inf)[0]
    else:
        raise KineticlibError('VT transition with no change in vibrational level specified')


def raw_vt_integral_rigid_sphere_fho(T: float, deg: int, sigma: float, mass: float, beta: float,
                                    ve_before: float, ve_after: float, molecule_diss: float,
                                    i: int, delta: int, nokt: bool=False) -> float:
    """Calculates the generalized VT omega integral using the FHO probability and rigid sphere
    cross-section model for the following process: **M(i) + P -> M(i + delta) + P**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    molecule_diss : float
        the dissociation energy of the molecule which undergoes the transition (with no offset)
    i : int
        the vibrational level of the molecule
    delta : int
        the change in the vibrational level of the molecule
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the VT crosssection

    Raises
    ------
    KineticlibError
        if ``delta == 0``

    """
    if delta != 0:
        if delta == 1:
            mult = (i + 1)
        elif delta == -1:
            mult = i
        elif delta > 0:
            mult = prob.fact_div_fact(i, i + delta) / (factorial(delta) ** 2)
        else:
            mult = prob.fact_div_fact(i + delta, i) / (factorial(-delta) ** 2)

        if not nokt:
            mult *= ((T * constants.pi * constants.k / (2.0 * mass)) ** 0.5)
        else:
            mult *= ((0.5 * constants.pi / mass) ** 0.5)

        svt = prob.svt(delta)
        f = lambda g: prob.vt_prob_g_only_fho(g, T, mass, beta, ve_before, ve_after,
                                              i, delta, molecule_diss, svt)\
                    * elastic_omega_g_only_rigid_sphere(g, deg)
        return mult * (sigma ** 2) * integrate.quad(f, 0, np.inf)[0]
    else:
        raise KineticlibError('VT transition with no change in vibrational level specified')


def raw_vv_integral_gss_fho(T: float, deg: int, mass: float, beta: float, gssc1: float, gssc2: float,
                            gsso1: float, gsso2: float, ve_before1: float, ve_after1: float,
                            ve_before2: float, ve_after2: float, i: int, k: int,
                            i_delta: int, nokt=False) -> float:
    """Calculates the generalized VV omega integral using the FHO probability and GSS
    cross-section model for the following process:
    **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    gssc1 : float
        the elastic crosssection GSS potential :math:`C_{1}` parameter
    gssc2 : float
        the elastic crosssection GSS potential :math:`C_{2}` parameter
    gsso1 : float
        the elastic crosssection GSS potential :math:`\\omega_{1}` parameter
    gsso2 : float
        the elastic crosssection GSS potential :math:`\\omega_{2}` parameter
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the VV crosssection

    Raises
    ------
    KineticlibError
        if ``i_delta == 0``
    """
    if i_delta != 0:

        if i_delta == 1:
            mult = (i + 1) * k
        elif i_delta == -1:
            mult = i * (k + 1)
        elif i_delta > 0:
            mult = prob.fact_div_fact(i, i + i_delta) * prob.fact_div_fact(k - i_delta, k) / (factorial(i_delta) ** 2)
        else:
            mult = prob.fact_div_fact(i + i_delta, i) * prob.fact_div_fact(k, k - i_delta) / (factorial(-i_delta) ** 2)

        if not nokt:
            mult *= (constants.physical_constants['Angstrom star'][0] ** 2)\
                    * ((T * constants.k / (2.0 * constants.pi * mass)) ** 0.5)
        else:
            mult *= (constants.physical_constants['Angstrom star'][0] ** 2)\
                    * ((0.5 / (constants.pi * mass)) ** 0.5)

        svv = prob.svv(i_delta)
        f1 = lambda g: prob.vv_prob_g_only_fho(g, T, mass, beta, ve_before1, ve_after1, ve_before2, ve_after2,
                                               i, k, i_delta, svv) * elastic_omega_g_only_vss(g, deg, -gsso1)
        f2 = lambda g: prob.vv_prob_g_only_fho(g, T, mass, beta, ve_before1, ve_after1, ve_before2, ve_after2,
                                               i, k, i_delta, svv) * elastic_omega_g_only_vss(g, deg, -gsso2)
        return mult * (gssc1 * ((constants.k * T) ** gsso1) * integrate.quad(f1, 0, np.inf)[0] +
                       gssc2 * ((constants.k * T) ** gsso2) * integrate.quad(f2, 0, np.inf)[0])
    else:
        raise KineticlibError('VV transition with no change in vibrational level specified')


def raw_vv_integral_vss_fho(T: float, deg: int, mass: float, beta: float, vssc: float, vsso: float,
                            ve_before1: float, ve_after1: float, ve_before2: float, ve_after2: float, i: int, k: int,
                            i_delta: int, nokt=False) -> float:
    """Calculates the generalized VV omega integral using the FHO probability and VSS
    cross-section model for the following process:
    **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the VV crosssection

    Raises
    ------
    KineticlibError
        if ``i_delta == 0``
    """
    if i_delta != 0:

        if i_delta == 1:
            mult = (i + 1) * k
        elif i_delta == -1:
            mult = i * (k + 1)
        elif i_delta > 0:
            mult = prob.fact_div_fact(i, i + i_delta) * prob.fact_div_fact(k - i_delta, k) / (factorial(i_delta) ** 2)
        else:
            mult = prob.fact_div_fact(i + i_delta, i) * prob.fact_div_fact(k, k - i_delta) / (factorial(-i_delta) ** 2)

        if not nokt:
            mult *= (constants.physical_constants['Angstrom star'][0] ** 2)\
                    * ((T * constants.k / (2.0 * constants.pi * mass)) ** 0.5)
        else:
            mult *= (constants.physical_constants['Angstrom star'][0] ** 2)\
                    * ((0.5 / (constants.pi * mass)) ** 0.5)

        svv = prob.svv(i_delta)
        f = lambda g: prob.vv_prob_g_only_fho(g, T, mass, beta, ve_before1, ve_after1, ve_before2, ve_after2,
                                              i, k, i_delta, svv) * elastic_omega_g_only_vss(g, deg, vsso)
        return mult * vssc * (T ** (-vsso)) * integrate.quad(f, 0, np.inf)[0]
    else:
        raise KineticlibError('VV transition with no change in vibrational level specified')


def raw_vv_integral_rigid_sphere_fho(T: float, deg: int, sigma: float, mass: float, beta: float,
                                     ve_before1: float, ve_after1: float, ve_before2: float, ve_after2: float,
                                     i: int, k: int, i_delta: int, nokt=False) -> float:
    """Calculates the generalized VV omega integral using the FHO probability and
    rigid sphere cross-section model for the following process:
    **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    beta : float
        the IPL potential :math:`\\beta` parameter
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the VV crosssection

    Raises
    ------
    KineticlibError
        if ``i_delta == 0``
    """
    if i_delta != 0:

        if i_delta == 1:
            mult = (i + 1) * k
        elif i_delta == -1:
            mult = i * (k + 1)
        elif i_delta > 0:
            mult = prob.fact_div_fact(i, i + i_delta) * prob.fact_div_fact(k - i_delta, k) / (factorial(i_delta) ** 2)
        else:
            mult = prob.fact_div_fact(i + i_delta, i) * prob.fact_div_fact(k, k - i_delta) / (factorial(-i_delta) ** 2)

        if not nokt:
            mult *= ((T * constants.pi * constants.k / (2.0 * mass)) ** 0.5)
        else:
            mult *= ((0.5 * constants.pi / mass) ** 0.5)

        svv = prob.svv(i_delta)
        f = lambda g: prob.vv_prob_g_only_fho(g, T, mass, beta, ve_before1, ve_after1, ve_before2,
                                              ve_after2, i, k, i_delta, svv)\
                      * elastic_omega_g_only_rigid_sphere(g, deg)
        return mult * (sigma ** 2) * integrate.quad(f, 0, np.inf)[0]
    else:
        raise KineticlibError('VV transition with no change in vibrational level specified')


def raw_diss_integral_gss(T: float, deg: int, mass: float, gssc1: float, gssc2: float,
                          gsso1: float, gsso2: float, molecule_vibr: float, molecule_diss: float,
                          center_of_mass: bool=True, vl_dependent: bool=True, nokt: bool=False) -> float:
    """Calculates the generalized dissociation omega integral using the GSS model, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    gssc1 : float
        the elastic crosssection GSS potential :math:`C_{1}` parameter
    gssc2 : float
        the elastic crosssection GSS potential :math:`C_{2}` parameter
    gsso1 : float
        the elastic crosssection GSS potential :math:`\\omega_{1}` parameter
    gsso2 : float
        the elastic crosssection GSS potential :math:`\\omega_{2}` parameter
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value) (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the dissociation crosssection
    """
    if vl_dependent:
        min_sq = (molecule_diss - molecule_vibr) / (constants.k * T)
    else:
        min_sq = molecule_diss / (constants.k * T)


    min_g = min_sq ** 0.5
    f = lambda g: raw_crosssection_diss_gss(g, T, gssc1, gssc2, gsso1, gsso2, molecule_vibr, molecule_diss,
                                            center_of_mass, vl_dependent)\
                  * (g ** (3.0 + 2.0 * deg)) * exp(-g ** 2)
    if not nokt:
        return (constants.physical_constants['Angstrom star'][0] ** 2) *\
               ((constants.k * T / (2 * constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]
    else:
        return (constants.physical_constants['Angstrom star'][0] ** 2) *\
               ((0.5 / (constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]


def raw_diss_integral_vss(T: float, deg: int, mass: float, vssc: float, vsso: float,
                          molecule_vibr: float, molecule_diss: float, center_of_mass: bool=True,
                          vl_dependent: bool=True, nokt: bool=False) -> float:
    """Calculates the generalized dissociation omega integral using the VSS model, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value) (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the dissociation crosssection
    """
    if vl_dependent:
        min_sq = (molecule_diss - molecule_vibr) / (constants.k * T)
    else:
        min_sq = molecule_diss / (constants.k * T)


    min_g = min_sq ** 0.5
    f = lambda g: raw_crosssection_diss_vss(g, T, vssc, vsso, molecule_vibr, molecule_diss,
                                            center_of_mass, vl_dependent)\
                  * (g ** (3.0 + 2.0 * deg)) * exp(-g ** 2)
    if not nokt:
        return (constants.physical_constants['Angstrom star'][0] ** 2) *\
               ((constants.k * T / (2 * constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]
    else:
        return (constants.physical_constants['Angstrom star'][0] ** 2) *\
               ((0.5 / (constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]


def raw_diss_integral_rigid_sphere(T: float, deg: int, sigma: float, mass: float,
                                   molecule_vibr: float, molecule_diss: float, center_of_mass: bool=True,
                                   vl_dependent: bool=True, nokt: bool=False) -> float:
    """Calculates the generalized dissociation omega integral either using the rigid sphere
    model, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value) (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the dissociating
        molecule, if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the dissociation crosssection
    """
    if vl_dependent:
        min_sq = (molecule_diss - molecule_vibr) / (constants.k * T)
    else:
        min_sq = molecule_diss / (constants.k * T)

    if center_of_mass:

        min_g = min_sq ** 0.5
        f = lambda g: raw_crosssection_diss_rigid_sphere(g, T, sigma, molecule_vibr, molecule_diss,
                                                         center_of_mass, vl_dependent)\
                      * (g ** (3.0 + 2.0 * deg)) * exp(-g ** 2)
        if not nokt:
            return ((constants.k * T / (2 * constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]
        else:
            return ((0.5 / (constants.pi * mass)) ** 0.5) * integrate.quad(f, min_g, np.inf)[0]
    else:
        if not nokt:
            multiplier = ((constants.k * T / (2 * constants.pi * mass)) ** 0.5)
        else:
            multiplier = ((0.5 / (constants.pi * mass)) ** 0.5)

        if deg == 0:
            return 0.5 * constants.pi * (sigma ** 2) * multiplier * (min_sq + 1.0) * exp(-min_sq)
        elif deg == 1:
            return 0.5 * constants.pi * (sigma ** 2) * multiplier * (min_sq ** 2 + 2.0 * min_sq + 2.0) * exp(-min_sq)
        else:
            min_g = min_sq ** 0.5
            f = lambda g: raw_crosssection_diss_rigid_sphere(g, T, sigma, molecule_vibr, molecule_diss,
                                                             center_of_mass, vl_dependent)\
                          * (g ** (3.0 + 2.0 * deg)) * exp(-g ** 2)
            if not nokt:
                return multiplier * integrate.quad(f, min_g, np.inf)[0]
            else:
                return multiplier * integrate.quad(f, min_g, np.inf)[0]


def raw_elastic_integral_gss(T: float, deg: int, mass: float, gssc1: float, gssc2: float, gsso1: float, gsso2: float,
                             nokt: bool=False) -> float:
    """Calculates the generalized elastic omega integral using the GSS model,
    *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    gssc1 : float
        the elastic crosssection GSS potential :math:`C_{1}` parameter
    gssc2 : float
        the elastic crosssection GSS potential :math:`C_{2}` parameter
    gsso1 : float
        the elastic crosssection GSS potential :math:`\\omega_{1}` parameter
    gsso2 : float
        the elastic crosssection GSS potential :math:`\\omega_{2}` parameter
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the elastic crosssection
    """
    if not nokt:
        multiplier = ((T * constants.k / (2.0 * constants.pi * mass)) ** 0.5)
    else:
        multiplier = ((0.5 / (constants.pi * mass)) ** 0.5)
    return 0.5 * multiplier * (constants.physical_constants['Angstrom star'][0] ** 2)\
               * (gamma(2.0 + gsso1 + deg) * gssc1 * ((constants.k * T) ** gsso1)
                  + gamma(2.0 + gsso2 + deg) * gssc2 * ((constants.k * T) ** gsso2))


def raw_elastic_integral_vss(T: float, deg: int, mass: float, vssc: float, vsso: float, nokt: bool=False) -> float:
    """Calculates the generalized elastic omega integral using the VSS model,
    *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    vssc : float
        the elastic crosssection VSS potential :math:`C` parameter
    vsso : float
        the elastic crosssection VSS potential :math:`\\omega` parameter
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the elastic crosssection
    """
    if not nokt:
        multiplier = ((T * constants.k / (2.0 * constants.pi * mass)) ** 0.5)
    else:
        multiplier = ((0.5 / (constants.pi * mass)) ** 0.5)
    return 0.5 * multiplier * gamma(2.0 - vsso + deg) * (constants.physical_constants['Angstrom star'][0] ** 2)\
               * vssc * (T ** (-vsso))


def raw_elastic_integral_rigid_sphere(T: float, deg: int, sigma: float, mass: float, nokt: bool=False) -> float:
    """Calculates the generalized elastic omega integral using the rigid sphere model,
    *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    deg : int
        the degree of the omega integral
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The generalized omega integral over the elastic crosssection
    """
    if not nokt:
        multiplier = ((T * constants.k / (2.0 * constants.pi * mass)) ** 0.5)
    else:
        multiplier = ((0.5 / (constants.pi * mass)) ** 0.5)
    return 0.5 * multiplier * constants.pi * gamma(0.5 * deg + 2.0) * (sigma ** 2)


def raw_dE_rot_sq_equiprob(T: float, Z_rot: float, molecule_rot_symmetry: float, molecule_rot_const: float,
                           molecule_num_rot: int) -> float:
    """Calculates the partial averaging of the squared change in rotational energy
    over all one-quantum rotational transitions
    :math:`\\left<\\left(\\Delta \\mathcal{E}^{rot}_{c}\\right)^{2}\\right>_{part}`,
    considering all one-quantum transitions to be equiprobable, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    Z_rot : float
        the value of the rotational partition function of the molecule
    molecule_rot_symmetry : float
        should equal 2.0 if the molecule is homonuclear and 1.0 otherwise
    molecule_rot_const : float
        the quantity :math:`h ^ 2 / (8 \\pi ^ 2 I_{rot,c})`, where :math:`I_{rot,c}` is the moment of rotational
        inertia of the molecule
    molecule_num_rot : int
        the amount of rotational levels in the molecule

    Returns
    -------
    float
        The calculated averaging
    """
    A = constants.k * T / molecule_rot_const
    Asqrt = A ** 0.5
    molecule_num_rot_sq = molecule_num_rot * molecule_num_rot
    prettyexp = exp(-(-1.0 + molecule_num_rot) * molecule_num_rot / A)
    prettyexp2 = exp(0.25 * ((1.0 - 2.0 * molecule_num_rot) ** 2) / A)
    prettyexp3 = exp(0.25 * ((1.0 + 2.0 * molecule_num_rot) ** 2) / A)
    prettyexp4 = exp(-(1.0 + molecule_num_rot) * molecule_num_rot / A)
    prettyerf = erf(0.5 / Asqrt)
    prettyerf2 = erf((-1.0 + 2 * molecule_num_rot) / (2.0 * Asqrt))
    prettyerf3 = erf((1.0 + 2 * molecule_num_rot) / (2.0 * Asqrt))
    prettyerf4 = erf(1.5 / Asqrt)

    tmp = 0.5 * A * prettyexp\
              * (2.0 * (A - 4 * A * A + A * (5.0 + 4 * A) * exp((-1 + molecule_num_rot) * molecule_num_rot / A)
                        - 2.0 * A * molecule_num_rot + 2.0 * molecule_num_rot_sq - 4 * A * molecule_num_rot_sq
                        - 2.0 * molecule_num_rot_sq * molecule_num_rot_sq) + Asqrt * (-1.0 + 6.0 * A)
                 * prettyexp2 * (constants.pi ** 0.5)
                 * (prettyerf2 - prettyerf))

    tmp += 2.0 * (A ** 3) - A * prettyexp * (2.0 * A * A + 2.0 * A * (-1.0 + molecule_num_rot) * molecule_num_rot
                                             + ((-1.0 + molecule_num_rot) ** 2) * molecule_num_rot_sq)
    tmp += 0.5 * (2.0 * A * (4.0 + 9.0 * A + 2.0 * A * A) - 3.0 * (A ** 1.5)
                  * (1.0 + 2.0 * A) * exp(0.25 / A) * (constants.pi ** 0.5) * prettyerf
                  - A * prettyexp * (2.0 * (2.0 * A * A + molecule_num_rot_sq * ((1.0 + molecule_num_rot) ** 2)
                                            + A * (3.0 + 4.0 * molecule_num_rot + 2.0 * molecule_num_rot_sq))
                                     - 3.0 * Asqrt * (1.0 + 2.0 * A) * prettyexp2 * (constants.pi ** 0.5) * prettyerf2))

    tmp += 0.5 * A * (exp(-0.5 / A) * (2.0 * A * (1.0 + 4.0 * A)
                                          + Asqrt * (-1.0 + 6.0 * A) * exp(2.25 / A) * (constants.pi ** 0.5)
                                          * prettyerf4)
                      - prettyexp4
                      * (8.0 * A * A + 4.0 * molecule_num_rot_sq * (-1.0 * molecule_num_rot_sq)
                         + A * (-2.0 - 4.0 * molecule_num_rot + 8.0 * molecule_num_rot_sq)
                         + Asqrt * (-1.0 + 6.0 * A) * prettyexp3 * (constants.pi ** 0.5) * prettyerf3))
    tmp += 2.0 * A * (2.0 + 2.0 * A + A * A)\
               * exp(-2.0 / A) - A * prettyexp4\
                                      * (2.0 * A * A + 2 * A * molecule_num_rot
                                             * (1.0 + molecule_num_rot)
                                         + molecule_num_rot_sq * (1.0 + molecule_num_rot) * (1.0 + molecule_num_rot))
    tmp += 0.5 * (A * Asqrt * (1.0 + 2.0 * A) * exp(-2.0 / A)
                  * (2.0 * Asqrt + 3.0 * exp(2.25 / A) * (constants.pi ** 0.5) * prettyerf4)
                  + prettyexp4 * (-2.0 * A * (2.0 * A * A + (-1.0 + molecule_num_rot)
                                              * (-1.0 + molecule_num_rot) * molecule_num_rot_sq
                                              + A * (3.0 + 2.0 * (-2.0 + molecule_num_rot) * molecule_num_rot))
                                  - 3.0 * A * Asqrt * (1.0 + 2.0 * A) * prettyexp3
                                  * (constants.pi ** 0.5) * prettyerf3))
    tmp *= (molecule_rot_const ** 2) / molecule_rot_symmetry

    return 0.5 * tmp / (Z_rot * ((constants.k * T) ** 2) * molecule_num_rot)


def raw_dE_rot_single_equiprob(T: float, Z_rot: float, molecule_rot_symmetry: float,
                               molecule_rot_const: float, molecule_num_rot: int) -> float:
    """Calculates the partial averaging of the change in rotational energy
    over all one-quantum rotational transitions
    :math:`\\left<\\Delta \\mathcal{E}^{rot}_{c}\\right>_{part}`,
    considering all one-quantum transitions to be equiprobable, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    Z_rot : float
        the value of the rotational partition function of the molecule
    molecule_rot_symmetry : float
        should equal 2.0 if the molecule is homonuclear and 1.0 otherwise
    molecule_rot_const : float
        the quantity :math:`h ^ 2 / (8 \\pi ^ 2 I_{rot,c})`, where :math:`I_{rot,c}` is the moment of rotational
        inertia of the molecule
    molecule_num_rot : int
        the amount of rotational levels in the molecule

    Returns
    -------
    float
        The calculated averaging
    """
    A = constants.k * T / molecule_rot_const
    Asqrt = A ** 0.5
    prettyexp = exp(-molecule_num_rot * (molecule_num_rot - 1) / A)

    tmp = A * (A - prettyexp * (A + molecule_num_rot ** 2 - molecule_num_rot))
    tmp -= prettyexp * (A * (A + 2.0) / prettyexp - A * (A + molecule_num_rot + molecule_num_rot ** 2)
                        + (A ** 1.5) * exp(((1.0 - 2.0 * molecule_num_rot) ** 2) / (4.0 * A))
                        * (constants.pi ** 0.5) * (-erf(0.5 / Asqrt)
                                                   + erf((-1.0 + 2 * molecule_num_rot) / (2.0 * Asqrt))))
    tmp += A * ((A + 2.0) * exp(-2.0 / A) - exp(-molecule_num_rot * (molecule_num_rot + 1) / A)
                          * (A + molecule_num_rot ** 2 + molecule_num_rot))
    tmp -= A * (exp(-2.0 / A) * (A + (Asqrt * exp(2.25 / A)) * (constants.pi ** 0.5)
                * erf(1.5 / Asqrt)) - exp(-molecule_num_rot * (1.0 + molecule_num_rot) / A)
                * (A + (-1.0 + molecule_num_rot) * molecule_num_rot + Asqrt
                   * exp(((1.0 + 2.0 * molecule_num_rot) ** 2) / (4.0 * A))
                   * (constants.pi ** 0.5) * erf((1.0 + 2.0 * molecule_num_rot) / (2.0 * Asqrt))))
    tmp *= molecule_rot_const / molecule_rot_symmetry

    return 0.5 * tmp / (Z_rot * constants.k * T * molecule_num_rot)
