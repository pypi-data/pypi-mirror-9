"""Contains functions for calculating generalized affinities and equilibrium concentrations in binary mixtures"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

from scipy import constants
from scipy.optimize import brentq
from .particles import Atom, MoleculeMultiT, MoleculeQuasi, MoleculeOneT, Molecule
from .errors import KineticlibError
from math import exp


def Gamma_vt_sts(T: float, molecule: Molecule, i: int, delta: int, ni_before: float, ni_after: float) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{VT}` for a VT transition:
    **M(i) + P -> M(i+delta) + P** in the state-to-state approximation

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule : Molecule
        the molecule undergoing the transition
    i : int
        the vibrational level of the molecule before the transition
    delta : int
        the change in vibrational level of the molecule undergoing the transition
    ni_before : float
        the numeric density of molecules of species M at the original vibrationa level (before the transition)
    ni_after : float
        the numeric density of molecules of species M at the new vibrational level (after the transition)

    Returns
    -------
    float
        The generalized thermodynamic force for a VT transition

    """
    return raw_Gamma_vt_sts(T, molecule.vibr[i], molecule.vibr[i + delta], ni_before, ni_after)


def Gamma_vt(T: float, T1: float, molecule: MoleculeMultiT, delta: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{VT}` for a VT transition:
    **M(i) + P -> M(i+delta) + P** in the multi-temperature approximation

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule undergoing the transition
    molecule : MoleculeMultiT
        the molecule undergoing the transition
    delta : int
        the change in vibrational level of the molecule undergoing the transition

    Returns
    -------
    float
        The generalized thermodynamic force for a VT transition

    """
    return raw_Gamma_vt(T, T1, molecule.vibr[1], delta)


def Gamma_vv_sts(T: float, molecule1: Molecule, molecule2: Molecule, i: int, k: int, i_delta: int,
                 k_delta: int, ni_before1: float, ni_before2: float, ni_after1: float, ni_after2: float) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{VV}` for a VV transition:
    **M1(i) + M2(k) -> M1(i+i_delta) + M2(k+k_delta)** in the state-to-state approximation

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule1 : Molecule
        the molecule M1
    molecule2 : Molecule
        the molecule M2
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1
    k_delta : int
        the change in vibrational level of molecule M2
    ni_before1 : float
        the numeric density of molecules of species M1 at the original vibrationa level (before the transition)
    ni_before2 : float
        the numeric density of molecules of species M2 at the original vibrationa level (before the transition)
    ni_after1 : float
        the numeric density of molecules of species M1 at the new vibrational level (after the transition)
    ni_after2 : float
        the numeric density of molecules of species M2 at the new vibrational level (after the transition)

    Returns
    -------
    float
        The generalized thermodynamic force for a VV transition

    """
    return raw_Gamma_vv_sts(T, molecule1.vibr[i], molecule2.vibr[k],
                            molecule1.vibr[i + i_delta], molecule2.vibr[k + k_delta],
                            ni_before1, ni_before2, ni_after1, ni_after2)


def Gamma_vv(T: float, T1_1: float, T1_2: float, molecule1: MoleculeMultiT, molecule2: MoleculeMultiT, i_delta: int,
             k_delta: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{VV}` for a VV transition:
    **M1(i) + M2(k) -> M1(i+i_delta) + M2(k+k_delta)** in the multi-temperature approximation

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1_1 : float
        the temperature of the first vibrational level of the molecule M1
    T1_2 : float
        the temperature of the first vibrational level of the molecule M2
    molecule1 : MoleculeMultiT
        the molecule M1
    molecule2 : MoleculeMultiT
        the molecule M2
    i_delta : int
        the change in vibrational level of molecule M1
    k_delta : int
        the change in vibrational level of molecule M2

    Returns
    -------
    float
        The generalized thermodynamic force for a VV transition

    """
    return raw_Gamma_vv(T, T1_1, T1_2, molecule1.vibr[1], molecule2.vibr[1], i_delta, k_delta)


def Gamma_22_sts(T: float, molecule1: Molecule, molecule2: Molecule, molecule_new1: Molecule, molecule_new2: Molecule,
                 n_molecule1: float, n_molecule2: float, n_molecule_new1: float, n_molecule_new2: float,
                 i: int, k: int, i_new: int, k_new: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{2\\rightleftarrows2}` for a bimolecular
    exchange reaction in the state-to-state approximation:
    **M1(i) + M2(k) -> M3(i_new) + M4(k_new)**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule1 : Molecule
        the molecule M1
    molecule2 : Molecule
        the molecule M2
    molecule_new1 : Molecule
        the molecule M3
    molecule_new2 : Molecule
        the molecule M4
    n_molecule1 : float
        the numeric density of molecules of species M1 at the vibrationa level i
    n_molecule2 : float
        the numeric density of molecules of species M2 at the vibrationa level k
    n_molecule_new1 : float
        the numeric density of molecules of species M3 at the vibrationa level i_new
    n_molecule_new2 : float
        the numeric density of molecules of species M4 at the vibrationa level k_new
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_new : int
        the vibrational level of molecule M3
    k_new : int
        the vibrational level of molecule M4

    Returns
    -------
    float
        The generalized thermodynamic force for a bimolecular chemical exchange reaction

    """
    return raw_Gamma_22_sts(T, molecule1.vibr[i], molecule2.vibr[k],
                            molecule_new1.vibr[i_new], molecule_new2.vibr[k_new],
                            molecule1.Z_rot(T), molecule2.Z_rot(T), molecule_new1.Z_rot(T), molecule_new2.Z_rot(T),
                            molecule1.mass, molecule2.mass, molecule_new1.mass, molecule_new2.mass,
                            molecule1.form, molecule2.form, molecule_new1.form, molecule_new2.form,
                            n_molecule1, n_molecule2, n_molecule_new1, n_molecule_new2)


def Gamma_22(T: float, T1_1: float, T1_2: float, T1_new1: float, T1_new2: float, molecule1: MoleculeQuasi,
             molecule2: MoleculeQuasi, molecule_new1: MoleculeQuasi, molecule_new2: MoleculeQuasi, n_molecule1: float,
             n_molecule2: float, n_molecule_new1: float, n_molecule_new2: float, i: int, k: int, i_new: int,
             k_new: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{2\\rightleftarrows2}` for a bimolecular
    exchange reaction:
    **M1(i) + M2(k) -> M3(i_new) + M4(k_new)**  in the multi and one-temperature approximations

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
    T1_new1 : float
        the temperature of the first vibrational level of the molecule M3 (if the one-temperature approximation
        is used, can be set to any value)
    T1_new2 : float
        the temperature of the first vibrational level of the molecule M4 (if the one-temperature approximation
        is used, can be set to any value)
    molecule1 : MoleculeMultiT or MoleculeOneT
        the molecule M1
    molecule2 : MoleculeMultiT or MoleculeOneT
        the molecule M2
    molecule_new1 : MoleculeMultiT or MoleculeOneT
        the molecule M3
    molecule_new2 : MoleculeMultiT or MoleculeOneT
        the molecule M4
    n_molecule1 : float
        the numeric density of molecules of species M1
    n_molecule2 : float
        the numeric density of molecules of species M2
    n_molecule_new1 : float
        the numeric density of molecules of species M3
    n_molecule_new2 : float
        the numeric density of molecules of species M4
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_new : int
        the vibrational level of molecule M3
    k_new : int
        the vibrational level of molecule M4

    Returns
    -------
    float
        The generalized thermodynamic force for a bimolecular chemical exchange reaction

    Raises
    ------
    KineticlibError
        If ``molecule1``, ``molecule2``, ``molecule_new1``, ``molecule_new2`` are of different types
    """
    if isinstance(molecule1, MoleculeMultiT) and isinstance(molecule2, MoleculeMultiT)\
            and isinstance(molecule_new1, MoleculeMultiT) and isinstance(molecule_new2, MoleculeMultiT):
        return raw_Gamma_22(T, T1_1, T1_2, T1_new1, T1_new2, molecule1.vibr_zero, molecule2.vibr_zero,
                            molecule_new1.vibr_zero, molecule_new2.vibr_zero,
                            molecule1.vibr[1], molecule2.vibr[1], molecule_new1.vibr[1],
                            molecule_new2.vibr[1], molecule1.Z_vibr(T, T1_1), molecule2.Z_vibr(T, T1_2),
                            molecule_new1.Z_vibr(T, T1_new1), molecule_new2.Z_vibr(T, T1_new2), molecule1.mass,
                            molecule2.mass, molecule_new1.mass, molecule_new2.mass, molecule1.form, molecule2.form,
                            molecule_new1.form, molecule_new2.form, n_molecule1, n_molecule2, n_molecule_new1,
                            n_molecule_new2, i, k, i_new, k_new)
    elif isinstance(molecule1, MoleculeOneT) and isinstance(molecule2, MoleculeOneT)\
            and isinstance(molecule_new1, MoleculeOneT) and isinstance(molecule_new2, MoleculeOneT):
        return raw_Gamma_22_oneT(T, molecule1.Z_vibr(T), molecule2.Z_vibr(T),
                                 molecule_new1.Z_vibr(T), molecule_new2.Z_vibr(T), molecule1.mass,
                                 molecule2.mass, molecule_new1.mass, molecule_new2.mass, molecule1.form, molecule2.form,
                                 molecule_new1.form, molecule_new2.form, n_molecule1, n_molecule2, n_molecule_new1,
                                 n_molecule_new2)
    else:
        raise KineticlibError('Types of molecules do not match!')


def Gamma_diss_sts(T: float, molecule: Molecule, atom1: Atom, atom2: Atom,
                   n_molecule: float, n_atom1: float, n_atom2: float, diss_level: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{diss}` for a dissociation reaction:
    **AB(diss_level) + P -> A + B + P** in the state-to-state approximation

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule : Molecule
        the molecule which dissociates
    atom1 : Atom
        atom of the first atomic species which make up the molecule
    atom2 : Atom
        atom of the second atomic species which make up the molecule
    n_molecule : float
        the numeric density of molecules of species M at the vibrational level diss_level
    n_atom1 : float
        the numeric density of atoms of species atom1
    n_atom2 : float
        the numeric density of atoms of species atom2
    diss_level : int
        the vibrational level from which the molecule dissociates

    Returns
    -------
    float
        The generalized thermodynamic force for a dissociation reaction

    """
    return raw_Gamma_diss_sts(T, molecule.vibr[diss_level], molecule.Z_rot(T), molecule.mass, atom1.mass,
                              atom2.mass, molecule.diss, n_molecule, n_atom1, n_atom2)


def Gamma_diss(T: float, T1: float, molecule: MoleculeQuasi, atom1: Atom, atom2: Atom, n_molecule: float,
               n_atom1: float, n_atom2: float, diss_level: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{diss}` for a dissociation reaction:
    **AB(diss_level) + P -> A + B + P** in the multi and one-temperature approximations

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule which dissociates (if the one-temperature
        approximation is used, can be set to any value)
    molecule : MoleculeMultiT or MoleculeOneT
        the molecule which dissociates
    atom1 : Atom
        atom of the first atomic species which make up the molecule
    atom2 : Atom
        atom of the second atomic species which make up the molecule
    n_molecule : float
        the numeric density of molecules of species M
    n_atom1 : float
        the numeric density of atoms of species atom1
    n_atom2 : float
        the numeric density of atoms of species atom2
    diss_level : int
        the vibrational level from which the molecule dissociates (for a one-temperature aprroximation,
        where T=T1, this parameter plays no role and can be chosen arbitrarily)
        
    Returns
    -------
    float
        The generalized thermodynamic force for a dissociation reaction

    """
    if isinstance(molecule, MoleculeMultiT):
        return raw_Gamma_diss(T, T1, molecule.vibr[1], molecule.Z_int(T, T1), molecule.mass,
                              atom1.mass, atom2.mass, molecule.diss - molecule.vibr_zero,
                              n_molecule, n_atom1, n_atom2, diss_level)
    else:
        return raw_Gamma_diss_oneT(T, molecule.Z_int(T), molecule.mass, atom1.mass, atom2.mass,
                                   molecule.diss, n_molecule, n_atom1, n_atom2)


def find_natom_diss_eq(T: float, molecule: MoleculeOneT, atom: Atom, n: float, relative: bool=True) -> float:
    """Finds the numeric density of atoms in a binary mixture (A2, A) in vibrational equilibrium (a one-temperature
    distribution is used) at which chemical equilibrium occurs (:math:`\\Gamma^{diss} = 0`)

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule : MoleculeOneT
        the molecule which dissociates
    atom : Atom
        atom of the atomic species which make up the molecule
    n : float
        the total numeric density of the mixture
    relative : bool, optional
        if True, the function returns the relative numeric density of the atomic species, if False,
        the function returns the absolute numeric density of the atomic species, defaults to True

    Returns
    -------
    float
        Numeric density of atoms at which chemical equilibrium occurs in the mixture
    """
    return raw_find_natom_diss_eq(T, molecule.Z_int(T), molecule.mass, atom.mass, molecule.diss, n, relative)


def raw_Gamma_vt_sts(T: float, ve_before: float, ve_after: float, ni_before: float, ni_after: float) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{VT}` for a VT transition:
    **M(i) + P -> M(i+delta) + P** in the state-to-state approximation, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    ve_before : float
        the vibrational energy of the molecule before the transition
    ve_after : float
        the vibrational energy of the molecule after the transition
    ni_before : float
        the numeric density of molecules of species M at the original vibrationa level (before the transition)
    ni_after : float
        the numeric density of molecules of species M at the new vibrational level (after the transition)

    Returns
    -------
    float
        The generalized thermodynamic force for a VT transition

    """
    return 1.0 - ni_after * exp((ve_after - ve_before) / (constants.k * T)) / ni_before


def raw_Gamma_vt(T: float, T1: float, vibr_one: float, delta: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{VT}` for a VT transition:
    **M(i) + P -> M(i+delta) + P** in the multi-temperature approximation, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule undergoing the transition
    vibr_one : float
        the dimensional energy of the first vibrational level of the molecule undergoing the transition
    delta : int
        the change in vibrational level of the molecule undergoing the transition

    Returns
    -------
    float
        The generalized thermodynamic force for a VT transition

    """
    return 1.0 - exp((vibr_one * delta * (1.0 / T - 1.0 / T1)) / constants.k)


def raw_Gamma_vv_sts(T: float, ve_before1: float, ve_before2: float, ve_after1: float, ve_after2: float,
                     ni_before1: float, ni_before2: float, ni_after1: float, ni_after2: float) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{VV}` for a VV transition:
    **M1(i) + M2(k) -> M1(i+i_delta) + M2(k+k_delta)** in the state-to-state approximation, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    ve_before1 : float
        the vibrational energy of the molecule M1 before the transition
    ve_before2 : float
        the vibrational energy of the molecule M2 before the transition
    ve_after1 : float
        the vibrational energy of the molecule M1 after the transition
    ve_after2 : float
        the vibrational energy of the molecule M2 after the transition
    ni_before1 : float
        the numeric density of molecules of species M1 at the original vibrationa level (before the transition)
    ni_before2 : float
        the numeric density of molecules of species M2 at the original vibrationa level (before the transition)
    ni_after1 : float
        the numeric density of molecules of species M1 at the new vibrational level (after the transition)
    ni_after2 : float
        the numeric density of molecules of species M2 at the new vibrational level (after the transition)

    Returns
    -------
    float
        The generalized thermodynamic force for a VV transition

    """
    return 1.0 - ni_after1 * ni_after2 * exp((ve_after1 + ve_after2 - ve_before1 - ve_before2) / (constants.k * T))\
                 / (ni_before1 * ni_before2)


def raw_Gamma_vv(T: float, T1_1: float, T1_2: float, vibr_one1: float, vibr_one2: float,
                 i_delta: int, k_delta: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{VV}` for a VV transition:
    **M1(i) + M2(k) -> M1(i+i_delta) + M2(k+k_delta)** in the multi-temperature approximation, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1_1 : float
        the temperature of the first vibrational level of the molecule M1
    T1_2 : float
        the temperature of the first vibrational level of the molecule M2
    vibr_one1 : float
        the dimensional energy of the first vibrational level of the molecule M1
    vibr_one2 : float
        the dimensional energy of the first vibrational level of the molecule M2
    i_delta : int
        the change in vibrational level of molecule M1
    k_delta : int
        the change in vibrational level of molecule M2

    Returns
    -------
    float
        The generalized thermodynamic force for a VV transition

    """
    add = i_delta * vibr_one1 * (1.0 - T / T1_1) + k_delta * vibr_one2 * (1.0 - T / T1_2)
    return 1.0 - exp(add / (constants.k * T))


def raw_Gamma_22_sts(T: float, ve_before1: float, ve_before2: float, ve_after1: float, ve_after2: float,
                     Z_rot1: float, Z_rot2: float, Z_rot_new1: float, Z_rot_new2: float,
                     mass1: float, mass2: float, mass_new1: float, mass_new2: float,
                     form1: float, form2: float, form_new1: float, form_new2: float,
                     n_molecule1: float, n_molecule2: float, n_molecule_new1: float, n_molecule_new2: float) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{2\\rightleftarrows2}` for a bimolecular
    exchange reaction in the state-to-state approximation:
    **M1(i) + M2(k) -> M3(i_new) + M4(k_new)**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    ve_before1 : float
        the vibrational energy of the molecule M1
    ve_before2 : float
        the vibrational energy of the molecule M2
    ve_after1 : float
        the vibrational energy of the molecule M3
    ve_after2 : float
        the vibrational energy of the molecule M4
    Z_rot1 : float
        the value of the rotational partition function of the molecule M1
    Z_rot2 : float
        the value of the rotational partition function of the molecule M2
    Z_rot_new1 : float
        the value of the rotational partition function of the molecule M3
    Z_rot_new2 : float
        the value of the rotational partition function of the molecule M4
    mass1 : float
        the mass of the molecule M1
    mass2 : float
        the mass of the molecule M2
    mass_new1 : float
        the mass of the molecule M3
    mass_new2 : float
        the mass of the molecule M4
    form1 : float
        the formation energy of the molecule M1
    form2 : float
        the formation energy of the molecule M2
    form_new1 : float
        the formation energy of the molecule M3
    form_new2 : float
        the formation energy of the molecule M4
    n_molecule1 : float
        the numeric density of molecules of species M1 at the vibrationa level i
    n_molecule2 : float
        the numeric density of molecules of species M2 at the vibrationa level k
    n_molecule_new1 : float
        the numeric density of molecules of species M3 at the vibrationa level i_new
    n_molecule_new2 : float
        the numeric density of molecules of species M4 at the vibrationa level k_new

    Returns
    -------
    float
        The generalized thermodynamic force for a bimolecular chemical exchange reaction

    """
    kT = constants.k * T
    add = Z_rot1 * Z_rot2 / (Z_rot_new1 * Z_rot_new2)
    add *= (n_molecule_new1 * n_molecule_new2) / (n_molecule1 * n_molecule2)
    add *= (mass1 * mass2 / (mass_new1 * mass_new2)) ** 1.5
    add *= exp((form_new1 + form_new2 - form1 - form2) / kT)
    add *= exp((ve_after1 + ve_after2 - ve_before1 - ve_before2) / kT)

    return 1.0 - add


def raw_Gamma_22(T: float, T1_1: float, T1_2: float, T1_new1: float, T1_new2: float,
                 vibr_zero1: float, vibr_zero2: float, vibr_zero_new1: float, vibr_zero_new2: float,
                 vibr_one1: float, vibr_one2: float,
                 vibr_one_new1: float, vibr_one_new2: float, Z_int1: float, Z_int2: float, Z_int_new1: float,
                 Z_int_new2: float, mass1: float, mass2: float, mass_new1: float, mass_new2: float, form1: float,
                 form2: float, form_new1: float, form_new2: float, n_molecule1: float, n_molecule2: float,
                 n_molecule_new1: float, n_molecule_new2: float, i: int, k: int, i_new: int, k_new: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{2\\rightleftarrows2}` for a bimolecular
    exchange reaction in the multi-temperature approximation:
    **M1(i) + M2(k) -> M3(i_new) + M4(k_new)**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1_1 : float
        the temperature of the first vibrational level of the molecule M1
    T1_2 : float
        the temperature of the first vibrational level of the molecule M2
    T1_new1 : float
        the temperature of the first vibrational level of the molecule M3
    T1_new2 : float
        the temperature of the first vibrational level of the molecule M4
    vibr_zero1 : float
        the dimensional non-zero energy of the 0 vibrational level of the molecule M1
    vibr_zero2 : float
        the dimensional non-zero energy of the 0 vibrational level of the molecule M2
    vibr_zero_new1 : float
        the dimensional non-zero energy of the 0 vibrational level of the molecule M3
    vibr_zero_new2 : float
        the dimensional non-zero energy of the 0 vibrational level of the molecule M4
    vibr_one1 : float
        the dimensional energy of the first vibrational level of the molecule M1
    vibr_one2 : float
        the dimensional energy of the first vibrational level of the molecule M2
    vibr_one_new1 : float
        the dimensional energy of the first vibrational level of the molecule M3
    vibr_one_new2 : float
        the dimensional energy of the first vibrational level of the molecule M4
    Z_int1 : float
        the value of the internal partition function of the molecule M1
    Z_int2 : float
        the value of the internal partition function of the molecule M2
    Z_int_new1 : float
        the value of the internal partition function of the molecule M3
    Z_int_new2 : float
        the value of the internal partition function of the molecule M4
    mass1 : float
        the mass of the molecule M1
    mass2 : float
        the mass of the molecule M2
    mass_new1 : float
        the mass of the molecule M3
    mass_new2 : float
        the mass of the molecule M4
    form1 : float
        the formation energy of the molecule M1
    form2 : float
        the formation energy of the molecule M2
    form_new1 : float
        the formation energy of the molecule M3
    form_new2 : float
        the formation energy of the molecule M4
    n_molecule1 : float
        the numeric density of molecules of species M1
    n_molecule2 : float
        the numeric density of molecules of species M2
    n_molecule_new1 : float
        the numeric density of molecules of species M3
    n_molecule_new2 : float
        the numeric density of molecules of species M4
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_new : int
        the vibrational level of molecule M3
    k_new : int
        the vibrational level of molecule M4

    Returns
    -------
    float
        The generalized thermodynamic force for a bimolecular chemical exchange reaction

    """
    kT = constants.k * T
    add = Z_int1 * Z_int2 / (Z_int_new1 * Z_int_new2)
    add *= (n_molecule_new1 * n_molecule_new2) / (n_molecule1 * n_molecule2)
    add *= (mass1 * mass2 / (mass_new1 * mass_new2)) ** 1.5
    add *= exp((form_new1 + form_new2 - form1 - form2 + vibr_zero_new1 + vibr_zero_new2
                  - vibr_zero1 - vibr_zero2) / kT)
    add *= exp(vibr_one1 * i * (1.0 / (constants.k * T1_1) - 1.0 / kT)
                  + vibr_one2 * k * (1.0 / (constants.k * T1_2) - 1.0 / kT)
                  - vibr_one_new1 * i_new * (1.0 / (constants.k * T1_new1) - 1.0 / kT)
                  - vibr_one_new2 * k_new * (1.0 / (constants.k * T1_new2) - 1.0 / kT))
    return 1.0 - add


def raw_Gamma_22_oneT(T: float, Z_int1: float, Z_int2: float, Z_int_new1: float, Z_int_new2: float,
                      mass1: float, mass2: float, mass_new1: float, mass_new2: float,
                      form1: float, form2: float, form_new1: float, form_new2: float,
                      n_molecule1: float, n_molecule2: float, n_molecule_new1: float, n_molecule_new2: float) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{2\\rightleftarrows2}` for a bimolecular
    exchange reaction in the one-temperature approximation:
    **M1(i) + M2(k) -> M3(i_new) + M4(k_new)**, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    Z_int1 : float
        the value of the internal partition function of the molecule M1
    Z_int2 : float
        the value of the internal partition function of the molecule M2
    Z_int_new1 : float
        the value of the internal partition function of the molecule M3
    Z_int_new2 : float
        the value of the internal partition function of the molecule M4
    mass1 : float
        the mass of the molecule M1
    mass2 : float
        the mass of the molecule M2
    mass_new1 : float
        the mass of the molecule M3
    mass_new2 : float
        the mass of the molecule M4
    form1 : float
        the formation energy of the molecule M1
    form2 : float
        the formation energy of the molecule M2
    form_new1 : float
        the formation energy of the molecule M3
    form_new2 : float
        the formation energy of the molecule M4
    n_molecule1 : float
        the numeric density of molecules of species M1
    n_molecule2 : float
        the numeric density of molecules of species M2
    n_molecule_new1 : float
        the numeric density of molecules of species M3
    n_molecule_new2 : float
        the numeric density of molecules of species M4

    Returns
    -------
    float
        The generalized thermodynamic force for a bimolecular chemical exchange reaction

    """
    kT = constants.k * T
    add = Z_int1 * Z_int2 / (Z_int_new1 * Z_int_new2)
    add *= (n_molecule_new1 * n_molecule_new2) / (n_molecule1 * n_molecule2)
    add *= (mass1 * mass2 / (mass_new1 * mass_new2)) ** 1.5
    add *= exp(form_new1 / kT + form_new2 / kT - form1 / kT - form2 / kT)
    return 1.0 - add


def raw_Gamma_diss_sts(T: float, molecule_vibr: float,
                       Z_rot: float, mass_molecule: float, mass_atom1: float, mass_atom2: float,
                       molecule_diss: float, n_molecule: float, n_atom1: float, n_atom2: float) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{diss}` for a dissociation reaction:
    **AB(diss_level) + P -> A + B + P** in the state-to-state approximation, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule_vibr : float
        the vibrational energy of the level from which the molecule dissociates
    Z_rot : float
        the value of the rotational partition function of the molecule which dissociates
    mass_molecule : float
        the mass of the molecule which dissociates
    mass_atom1 : float
        the mass of the first atom product of dissociation
    mass_atom2 : float
        the mass of the second atom product of dissociation
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    n_molecule : float
        the numeric density of molecules of species M at the vibrational level diss_level
    n_atom1 : float
        the numeric density of atoms of species atom1
    n_atom2 : float
        the numeric density of atoms of species atom2

    Returns
    -------
    float
        The generalized thermodynamic force for a dissociation reaction

    """
    add = Z_rot * (n_atom1 * n_atom2) * (constants.h ** 3)\
                                      * ((mass_molecule / (2.0 * mass_atom1 * mass_atom2 * constants.pi
                                                               * constants.k * T)) ** 1.5) / n_molecule
    add *= exp((molecule_diss - molecule_vibr) / (constants.k * T))
    return 1.0 - add


def raw_Gamma_diss(T: float, T1: float, vibr_one: float, Z_int: float, mass_molecule: float, mass_atom1: float,
                   mass_atom2: float, molecule_diss: float, n_molecule: float, n_atom1: float, n_atom2: float,
                   diss_level: int) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{diss}` for a dissociation reaction:
    **AB(diss_level) + P -> A + B + P** in the multi-temperature approximation, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule M
    vibr_one : float
        the dimensional energy of the first vibrational level of the molecule which dissociates (with offset)
    Z_int : float
        the value of the internal partition function of the molecule which dissociates
    mass_molecule : float
        the mass of the molecule which dissociates
    mass_atom1 : float
        the mass of the first atom product of dissociation
    mass_atom2 : float
        the mass of the second atom product of dissociation
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with offset)
    n_molecule : float
        the numeric density of molecules of species M
    n_atom1 : float
        the numeric density of atoms of species atom1
    n_atom2 : float
        the numeric density of atoms of species atom2
    diss_level : int
        the vibrational level from which the molecule dissociates

    Returns
    -------
    float
        The generalized thermodynamic force for a dissociation reaction

    """
    add = Z_int * (n_atom1 * n_atom2) * (constants.h ** 3)\
                                      * ((mass_molecule / (2.0 * mass_atom1 * mass_atom2 * constants.pi
                                                               * constants.k * T)) ** 1.5) / n_molecule
    add *= exp(molecule_diss / (constants.k * T) + vibr_one * ((1.0 / T1 - 1.0 / T) / constants.k)
               * diss_level)
    return 1.0 - add


def raw_Gamma_diss_oneT(T: float, Z_int: float, mass_molecule: float, mass_atom1: float, mass_atom2: float,
                        molecule_diss: float, n_molecule: float, n_atom1: float, n_atom2: float) -> float:
    """Calculates the generalized thermodynamic force :math:`\\Gamma^{diss}` for a dissociation reaction:
    **AB + P -> A + B + P** in the one-temperature approximation, *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    Z_int : float
        the value of the internal partition function of the molecule which dissociates
    mass_molecule : float
        the mass of the molecule which dissociates
    mass_atom1 : float
        the mass of the first atom product of dissociation
    mass_atom2 : float
        the mass of the second atom product of dissociation
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    n_molecule : float
        the numeric density of molecules of species M
    n_atom1 : float
        the numeric density of atoms of species atom1
    n_atom2 : float
        the numeric density of atoms of species atom2

    Returns
    -------
    float
        The generalized thermodynamic force for a dissociation reaction

    """
    add = Z_int * (n_atom1 * n_atom2) * (constants.h ** 3)\
                                      * ((mass_molecule / (2.0 * mass_atom1 * mass_atom2 * constants.pi
                                                               * constants.k * T)) ** 1.5) / n_molecule
    add *= exp(molecule_diss / (constants.k * T))
    return 1.0 - add


def raw_find_natom_diss_eq(T: float, Z_int: float, mass_molecule: float, mass_atom: float, molecule_diss: float,
                           n: float, relative: bool=True) -> float:
    """Finds the numeric density of atoms in a binary mixture (A2, A) in vibrational equilibrium (a one-temperature
    distribution is used) at which chemical equilibrium occurs (:math:`\\Gamma^{diss} = 0`), *raw* version

    Parameters
    ----------
    T : float
        the temperature of the mixture
    Z_int : float
        the value of the internal partition function of the molecule which dissociates
    mass_molecule : float
        the mass of the molecule which dissociates
    mass_atom : float
        the mass of the atomic species which make up the molecule
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    n : float
        the total numeric density of the mixture
    relative : bool, optional
        if True, the function returns the relative numeric density of the atomic species, if False,
        the function returns the absolute numeric density of the atomic species, defaults to True

    Returns
    -------
    float
        Numeric density of atoms at which chemical equilibrium occurs in the mixture
    """
    xatom = brentq(Gamma_diss_binary_equilibrium_xatom, 0, 1, xtol=0.00001, maxiter=1000,
                   args=(Z_int, mass_molecule, mass_atom, molecule_diss, T, n))
    if relative:
        return xatom
    else:
        return n * xatom


def Gamma_diss_binary_equilibrium_xatom(x_atom: float, Z_int: float, mass_molecule: float, mass_atom: float,
                                        molecule_diss: float, T: float, n: float) -> float:
    """A helper function, which calculates Gamma_diss (multiplied by the relative numeric density of the molecules)
    for a binary mixture (A2, A) in vibrational equilibrium (a one-temperature distribution is used): **2A + A -> 3A**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    x_atom : float
        the relative numeric density of atoms
    Z_int : float
        the value of the internal partition function of the molecule which dissociates
    mass_molecule : float
        the mass of the molecule which dissociates
    mass_atom : float
        the mass of the atomic species which make up the molecule
    molecule_diss : float
        the dissociation energy of the molecule which dissociates (with no offset)
    n : float
        the total numeric density of the mixture

    Returns
    -------
    float
        Gamma_diss multiplied by the numeric density of the molecules
    """
    mult = Z_int * n * (x_atom ** 2) * (constants.h ** 3)\
                                     * ((mass_molecule / (2.0 * mass_atom * mass_atom * constants.pi
                                                               * constants.k * T)) ** 1.5)\
                                     * exp(molecule_diss / (constants.k * T))
    return 1.0 - x_atom - mult