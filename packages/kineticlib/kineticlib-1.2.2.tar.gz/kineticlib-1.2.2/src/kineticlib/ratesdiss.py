"""Contains functions for calculating dissociation rates
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

import numpy as np
from scipy import constants
from .crosssection import diss_integral
from .particles import Molecule, MoleculeMultiT, Atom, MoleculeQuasi
from math import exp


def k_diss_eq(T: float, model_data: np.ndarray, molecule: Molecule) -> float:
    """Calculates the equilibrium dissociation rate constant using the Arrhenius model

    Parameters
    ----------
    T : float
        the temperature of the mixture
    model_data : 1-D array-like
        dissociation model data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which dissociates

    Returns
    -------
    float
        Equilibrium dissociation rate constant

    """
    return raw_k_diss_eq(T, model_data[0], model_data[1], molecule.diss)


def diss_rate_treanor_marrone_sts(T: float, model_data: np.ndarray, molecule: Molecule, i: int,
                                  model: str='D6k') -> float:
    """Calculates the state-to-state non-equilibrium dissociation rate constant using the Treanor-Marrone model

    Parameters
    ----------
    T : float
        the temperature of the mixture
    model_data : 1-D array-like
        dissociation model data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which dissociates
    i : int
        the vibrational level from which the molecule dissociates
    model : str
        the model for the `U` parameter to be used, possible values:

            * ``'inf'`` - the U parameter in the non-equilbrium factor
              will be equal to :math:`\\infty`
            * ``'D6k'`` - the U parameter in the non-equilbrium factor will be equal
              to :math:`D / 6k`, where :math:`D` is the dissociation energy of the molecule
            * ``'3T'`` - the U parameter in the non-equilbrium factor will be equal to :math:`3T`

        defaults to 'D6k'

    Returns
    -------
    float
        Non-equilibrium dissociation state-to-state rate constant

    """
    return raw_diss_rate_treanor_marrone_sts(T, model_data[0], model_data[1], molecule.Z_diss(T, i, model),
                                             molecule.diss)


def diss_rate_integral_sts(T: float, idata: np.ndarray, molecule: Molecule, i: int,
                           center_of_mass: bool=True, vl_dependent: bool=True, model: str='VSS') -> float:
    """Calculates the state-to-state non-equilibrium dissociation rate constant using the generalized
    omega integral over the VSS or rigid sphere crosssection

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which dissociates
    i : int
        the vibrational level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the
        dissociating molecule,
        if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    model : str, optional
        the elastic crosssection model to be used, possible values:
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
    float
        Non-equilibrium dissociation state-to-state rate constant
    """
    return 8. * diss_integral(T, 0, idata, molecule, i, center_of_mass, vl_dependent, model, False)


def rec_rate_treanor_marrone_sts(T: float, model_data: np.ndarray, molecule: Molecule, atom1: Atom, atom2: Atom,
                                 i: int, model: str='D6k') -> float:
    """Calculates the state-to-state recombination rate constant using the Treanor-Marrone model

    Parameters
    ----------
    T : float
        the temperature of the mixture
    model_data : 1-D array-like
        dissociation model data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which dissociates
    atom1 : Atom
        atom of the first atomic species which make up the molecule
    atom2 : Atom
        atom of the second atomic species which make up the molecule
    i : int
        the vibrational level from which the molecule dissociates
    model : str
        the model for the `U` parameter to be used, possible values:

            * ``'inf'`` - the U parameter in the non-equilbrium factor
              will be equal to :math:`\\infty`
            * ``'D6k'`` - the U parameter in the non-equilbrium factor will be equal
              to :math:`D / 6k`, where :math:`D` is the dissociation energy of the molecule
            * ``'3T'`` - the U parameter in the non-equilbrium factor will be equal to :math:`3T`

        defaults to 'D6k'

    Returns
    -------
    float
        Recombination state-to-state rate constant
    """
    if isinstance(molecule, MoleculeMultiT):
        return raw_rec_rate_treanor_marrone_sts(T, model_data[0], model_data[1], molecule.Z_diss(T, i, model),
                                                molecule.Z_rot(T), molecule.mass, atom1.mass, atom2.mass,
                                                molecule.vibr[i] + molecule.vibr_zero, molecule.diss)
    else:
        return raw_rec_rate_treanor_marrone_sts(T, model_data[0], model_data[1], molecule.Z_diss(T, i, model),
                                                molecule.Z_rot(T), molecule.mass, atom1.mass, atom2.mass,
                                                molecule.vibr[i], molecule.diss)


def rec_rate_integral_sts(T: float, idata: np.ndarray, molecule: Molecule, atom1: Atom, atom2: Atom, i: int,
                          center_of_mass: bool=True, vl_dependent: bool=True, model: str='VSS') -> float:
    """Calculates the state-to-state recombination rate constant using the generalized
    omega integral over the VSS or rigid sphere crosssection

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which dissociates
    atom1 : Atom
        atom of the first atomic species which make up the molecule
    atom2 : Atom
        atom of the second atomic species which make up the molecule
    i : int
        the vibrational level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value)
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the
        dissociating molecule,
        if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    model : str, optional
        the elastic crosssection model to be used, possible values:
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
    float
        Recombination state-to-state rate constant
    """
    if isinstance(molecule, MoleculeMultiT):
        mult = rec_rate_sts_multiplier(T, molecule.Z_rot(T), molecule.mass, atom1.mass,
                                       atom2.mass, molecule.vibr[i] + molecule.vibr_zero, molecule.diss)
    else:
        mult = rec_rate_sts_multiplier(T, molecule.Z_rot(T), molecule.mass, atom1.mass,
                                       atom2.mass, molecule.vibr[i], molecule.diss)
    return 8.0 * mult * diss_integral(T, 0, idata, molecule, i, center_of_mass, vl_dependent, model, False)


def diss_rate_treanor_marrone(T: float, T1: float, model_data: np.ndarray, molecule: MoleculeQuasi,
                              model: str='D6k') -> float:
    """Calculates the multi(one)-temperature non-equilibrium dissociation rate constant using the Treanor-Marrone model

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule which dissociates (if the one-temperature
        approximation is used, can be set to any value)
    model_data : 1-D array-like
        dissociation model data
    molecule : MoleculeMultiT or MoleculeOneT
        the molecule which dissociates
    model : str
        the model for the `U` parameter to be used, possible values:

            * 'inf' - the U parameter in the non-equilbrium factor
              will be equal to :math:`\\infty`
            * 'D6k' - the U parameter in the non-equilbrium factor will be equal
              to :math:`D / 6k`, where :math:`D` is the dissociation energy of the molecule
            * if equal to '3T', the U parameter in the non-equilbrium factor will be equal to :math:`3T`

        defaults to 'D6k'

    Returns
    -------
    float
        Non-equilibrium dissociation rate constant
    """
    res = 0.0
    if isinstance(molecule, MoleculeMultiT):
        for i in range(molecule.num_vibr_levels(T, T1, True) + 1):
            res += molecule.vibr_exp(T, T1, i) \
                   * raw_diss_rate_treanor_marrone_sts(T, model_data[0], model_data[1],
                                                       molecule.Z_diss(T, i, model), molecule.diss)
        return res / molecule.Z_vibr(T, T1)
    else:
        for i in range(molecule.num_vibr + 1):
            res += molecule.vibr_exp(T, i) \
                   * raw_diss_rate_treanor_marrone_sts(T, model_data[0], model_data[1],
                                                       molecule.Z_diss(T, i, model), molecule.diss)
        return res / molecule.Z_vibr(T)


def diss_rate_integral(T: float, T1: float, idata: np.ndarray, molecule: MoleculeQuasi,
                       center_of_mass: bool=True, vl_dependent: bool=True, model: str='VSS') -> float:
    """Calculates the multi(one)-temperature non-equilibrium dissociation rate constant using the generalized
    omega integral over the VSS or rigid sphere crosssection

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule which dissociates (if the one-temperature
        approximation is used, can be set to any value)
    idata : 1-D array-like
        the array of interaction data
    molecule : MoleculeMultiT or MoleculeOneT
        the molecule which dissociates
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the
        dissociating molecule,
        if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    model : str, optional
        the elastic crosssection model to be used, possible values:
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'
        
    Returns
    -------
    float
        Non-equilibrium dissociation rate constant
    """
    res = 0.0
    if isinstance(molecule, MoleculeMultiT):
        for i in range(molecule.num_vibr_levels(T, T1, True) + 1):
            res += molecule.vibr_exp(T, T1, i) \
                   * diss_integral(T, 0, idata, molecule, i, center_of_mass, vl_dependent, model, False)
        return 8.0 * res / molecule.Z_vibr(T, T1)
    else:
        for i in range(molecule.num_vibr + 1):
            res += molecule.vibr_exp(T, i) \
                   * diss_integral(T, 0, idata, molecule, i, center_of_mass, vl_dependent, model, False)
        return 8.0 * res / molecule.Z_vibr(T)


def rec_rate_treanor_marrone(T: float, T1: float, model_data: np.ndarray, molecule: MoleculeQuasi,
                             atom1: Atom, atom2: Atom, model: str='D6k') -> float:
    """Calculates the averaged recombination rate constant using the Treanor-Marrone model

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule which dissociates (if the one-temperature
        approximation is used, can be set to any value)
    model_data : 1-D array-like
        dissociation model data
    molecule : MoleculeMultiT or MoleculeOneT
        the molecule which dissociates
    atom1 : Atom
        atom of the first atomic species which make up the molecule
    atom2 : Atom
        atom of the second atomic species which make up the molecule
    model : str
        the model for the `U` parameter to be used, possible values:

            * ``'inf'`` - the U parameter in the non-equilbrium factor
              will be equal to :math:`\\infty`
            * ``'D6k'`` - the U parameter in the non-equilbrium factor will be equal
              to :math:`D / 6k`, where :math:`D` is the dissociation energy of the molecule
            * ``'3T'`` - the U parameter in the non-equilbrium factor will be equal to :math:`3T`

        defaults to 'D6k'

    Returns
    -------
    float
        Averaged recombination rate constant
    """
    res = 0.0
    if isinstance(molecule, MoleculeMultiT):
        for i in range(molecule.num_vibr_levels(T, T1, True) + 1):
            res += raw_rec_rate_treanor_marrone_sts(T, model_data[0], model_data[1],
                                                    molecule.Z_diss(T, i, model), molecule.Z_rot(T), molecule.mass,
                                                    atom1.mass, atom2.mass, molecule.vibr[i] + molecule.vibr_zero,
                                                    molecule.diss)
        return res
    else:
        for i in range(molecule.num_vibr + 1):
            res += raw_rec_rate_treanor_marrone_sts(T, model_data[0], model_data[1],
                                                    molecule.Z_diss(T, i, model), molecule.Z_rot(T), molecule.mass,
                                                    atom1.mass, atom2.mass, molecule.vibr[i],
                                                    molecule.diss)
        return res


def rec_rate_integral(T: float, T1: float, idata: np.ndarray, molecule: MoleculeQuasi, atom1: Atom, atom2: Atom,
                      center_of_mass: bool=True, vl_dependent: bool=True, model: str='VSS') -> float:
    """Calculates the averaged recombination rate constant using the generalized
    omega integral over the VSS or rigid sphere crosssection

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule which dissociates (if the one-temperature
        approximation is used, can be set to any value)
    idata : 1-D array-like
        the array of interaction data
    molecule : MoleculeMultiT or MoleculeOneT
        the molecule which dissociates
    atom1 : Atom
        atom of the first atomic species which make up the molecule
    atom2 : Atom
        atom of the second atomic species which make up the molecule
    center_of_mass : bool, optional
        if ``True``, the kinetic energy of the collision partners will be calculated along the center-of-mass line,
        if ``False``, the total kinetic energy will be used, defaults to ``True``
    vl_dependent : bool, optional
        if ``True``, the dissociation crosssection takes into account the vibrational energy of the
        dissociating molecule,
        if ``False``, the crosssection is independent of the vibrational energy, defaults to ``True``
    model : str, optional
        the elastic crosssection model to be used, possible values:
        
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
    float
        Averaged recombination rate constant
    """
    res = 0.0
    if isinstance(molecule, MoleculeMultiT):
        for i in range(molecule.num_vibr_levels(T, T1, True) + 1):
            res += rec_rate_sts_multiplier(T, molecule.Z_rot(T), molecule.mass, atom1.mass,
                                           atom2.mass, molecule.vibr[i] + molecule.vibr_zero, molecule.diss)\
                   * diss_integral(T, 0, idata, molecule, i, center_of_mass, vl_dependent, model, False)
    else:
        for i in range(molecule.num_vibr + 1):
            res += rec_rate_sts_multiplier(T, molecule.Z_rot(T), molecule.mass, atom1.mass,
                                           atom2.mass, molecule.vibr[i], molecule.diss)\
                   * diss_integral(T, 0, idata, molecule, i, center_of_mass, vl_dependent, model, False)
    return 8.0 * res


def raw_k_diss_eq(T: float, arrhenius_n: float, arrhenius_A: float, molecule_diss: float) -> float:
    """Calculates the equilibrium dissociation rate constant using the Arrhenius model, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    arrhenius_n : float
        Arrhenius model n parameter
    arrhenius_A : float
        Arrhenius model A parameter
    molecule_diss : float
        the dissociation energy of the molecule (with no offset)

    Returns
    -------
    float
        Equilibrium dissociation rate constant

    """
    return arrhenius_A * (T ** arrhenius_n) * exp(-molecule_diss / (constants.k * T))


def raw_diss_rate_treanor_marrone_sts(T: float, arrhenius_n: float, arrhenius_A: float, Z_diss: float,
                                      molecule_diss: float) -> float:
    """Calculates the state-to-state non-equilibrium dissociation rate constant using the Treanor-Marrone
    model, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    arrhenius_n : float
        Arrhenius model n parameter
    arrhenius_A : float
        Arrhenius model A parameter
    Z_diss : float
        the non-equilibrium factor
    molecule_diss : float
        the dissociation energy of the molecule (with no offset)

    Returns
    -------
    float
        Non-equilibrium dissociation rate constant

    """
    return Z_diss * raw_k_diss_eq(T, arrhenius_n, arrhenius_A, molecule_diss)


def raw_rec_rate_treanor_marrone_sts(T: float, arrhenius_n: float, arrhenius_A: float,
                                     Z_diss: float, Z_rot: float, mass_molecule: float, mass_atom1: float,
                                     mass_atom2: float, molecule_vibr: float, molecule_diss: float) -> float:
    """Calculates the state-to-state recombination rate constant using the Treanor-Marrone
    model, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    arrhenius_n : float
        Arrhenius model n parameter
    arrhenius_A : float
        Arrhenius model A parameter
    Z_diss : float
        the non-equilibrium factor
    Z_rot : float
        the value of the rotational partition function of the molecule which dissociates
    mass_molecule : float
        the mass of the molecule which dissociates
    mass_atom1 : float
        the mass of the first atom product of dissociation
    mass_atom2 : float
        the mass of the second atom product of dissociation
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)

    Returns
    -------
    float
        Recombination rate constant

    """
    return Z_rot * (constants.h ** 3) * ((mass_molecule / (2.0 * mass_atom1
                                                           * mass_atom2 * constants.pi * constants.k * T)) ** 1.5)\
           * exp(-(molecule_diss - molecule_vibr) / (constants.k * T))\
           * raw_diss_rate_treanor_marrone_sts(T, arrhenius_n, arrhenius_A, Z_diss, molecule_diss)


def rec_rate_sts_multiplier(T: float, Z_rot: float, mass_molecule: float, mass_atom1: float, mass_atom2: float,
                            molecule_vibr: float, molecule_diss: float):
    """Calculates the state-to-state recombination rate constant divided by the corresponding
    dissociation rate constant

    Parameters
    ----------
    T : float
        the temperature of the mixture
    Z_rot : float
        the value of the rotational partition function of the molecule which dissociates
    mass_molecule : float
        the mass of the molecule which dissociates
    mass_atom1 : float
        the mass of the first atom product of dissociation
    mass_atom2 : float
        the mass of the second atom product of dissociation
    molecule_vibr : float
        the dimensional vibrational energy of the level from which the molecule dissociates (if ``vl_dependent``
        is ``False``, can be any value) (with no offset)
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)

    Returns
    -------
    float
        Recombination rate constant divided by the corresponding dissociation rate constant
    """
    return Z_rot * (constants.h ** 3) * ((mass_molecule / (2.0 * mass_atom1
                                                           * mass_atom2 * constants.pi * constants.k * T)) ** 1.5)\
           * exp(-(molecule_diss - molecule_vibr) / (constants.k * T))
