"""Functions for calculations of heat capacities and other mixture properties
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"

from .particles import MoleculeMultiT, Atom, Molecule, MoleculeOneT
from scipy import constants


def dUdT_multiT(T: float, mixture_components_atoms: list, mixture_components_molecules: list) -> float:
    """Calculates the partial derivative of the internal energy of the mixture per unit of mass :math:`U` with respect
    to the flow temperature :math:`T` for a multi-temperature flow

    Parameters
    ----------
    T : float
        the temperature of the mixture
    mixture_components_atoms : list
        a list of iterables of the following form, corresponding to the atomic components of the flow:

            0. the ``Atom`` class instance
            #. the corresponding numeric density of the atomic species

    mixture_components_molecules : list
        a list of iterables of the following form, corresponding to the molecular components of the flow:

            0. the ``MoleculeMultiT`` class instance
            #. the corresponding numeric density of the molecular species
            #. the corresponding temperature of the first vibrational level of the molecule species

    Returns
    -------
    float
        The quantity :math:`\\partial U / \\partial T`
    """
    density = 0.0
    n = 0.0
    curr_dudt = 0.0
    for atom_component in mixture_components_atoms:
        density += atom_component[0].mass * atom_component[1]
        n += atom_component[1]

    for molecule_component in mixture_components_molecules:
        density += molecule_component[0].mass * molecule_component[1]
        n += molecule_component[1]

    for molecule_component in mixture_components_molecules:
        curr_dudt += (molecule_component[1] / density) * constants.k + \
                     (molecule_component[0].mass * molecule_component[1] / density)\
                     * molecule_component[0].E_vibr_dT(T, molecule_component[2])

    propmass = density / n
    return curr_dudt + 1.5 * constants.k / propmass


def dUdT1(T: float, T1: float, molecule: MoleculeMultiT, n_molecule: float, mixture_density: float) -> float:
    """Calculates the partial derivative of the internal energy of the mixture per unit of mass :math:`U` with respect
    to the temperature of the first vibrational level (of a molecular species :math:`c`) :math:`T_{1}^{c}`

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecular species with respect to which the derivative
        is being calculated
    molecule : MoleculeMultiT
        the molecule corresponding to the molecular species with respect to which the derivative is being calculated
    n_molecule : float
        the numeric density of the molecular species with respect to which the derivative is being calculated
    mixture_density : float
        the mass density of the mixture

    Returns
    -------
    float
        The quantity :math:`\\partial U / \\partial T_{1}^{c}`
    """
    return molecule.E_vibr_dT1(T, T1) * molecule.mass * n_molecule / mixture_density


def dUdn_atom(T: float, atom: Atom, mixture_density: float) -> float:
    """Calculates the partial derivative of the internal energy of the mixture per unit of mass :math:`U` with respect
    to the numeric density of an atomic species :math:`n_{c}`

    Parameters
    ----------
    T : float
        the temperature of the mixture
    atom : Atom
        the atom corresponding to the atomic species with respect to the numeric density of which the derivative
        is being calculated
    mixture_density : float
        the mass density of the mixture

    Returns
    -------
    float
        The quantity :math:`\\partial U / \\partial n_{c}`
    """
    return (1.5 * constants.k * T + atom.form) / mixture_density


def dUdn_molecule(T: float, T1: float, molecule: Molecule, mixture_density: float) -> float:
    """Calculates the partial derivative of the internal energy of the mixture per unit of mass :math:`U` with respect
    to the numeric density of a molecular species :math:`n_{c}`

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecular species with respect to the numeric density of
        which the derivative is being calculated (if the state-to-state or one-temperature approximation
        is used, can be set to any value)
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule corresponding to the molecular species with respect to the numeric density of which the derivative
        is being calculated
    mixture_density : float
        the mass density of the mixture

    Returns
    -------
    float
        The quantity :math:`\\partial U / \\partial n_{c}`
    """
    if isinstance(molecule, MoleculeMultiT):
        return (1.5 * constants.k * T + molecule.avg_rot_energy(T, True)
                + molecule.avg_vibr_energy(T, T1, True) + molecule.form) / mixture_density
    elif isinstance(molecule, MoleculeOneT):
        return (1.5 * constants.k * T + molecule.avg_rot_energy(T, True)
                + molecule.avg_vibr_energy(T, True) + molecule.form) / mixture_density
    else:
        return (1.5 * constants.k * T + molecule.avg_rot_energy(T, True) + molecule.form) / mixture_density