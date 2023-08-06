"""Contains functions for working with Waldman-Trubenbacher polynomials
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

from .particles import MoleculeMultiT, Molecule, MoleculeOneT


def wt_poly_norm_sts(T: float, molecule: Molecule) -> float:
    """Calculates the square of the "norm" of the Waldman Trubenbacher polynomial of the following form:
    :math:`P_{j} = -[\\varepsilon_{j} / kT]'`, where :math:`j` is the rotational level of the molecule,
    :math:`[A]' = A - <A>_{rot}`, where :math:`<>_{rot}`
    denotes averaging over the rotational spectrum.
    The square of the "norm" is defined as: :math:`||P_{j}||^{2} = \\left<P_{j}^{2} \\right>_{rot}`

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule : Molecule
        the molecule for which the polynomial is calculated

    Returns
    -------
    float
        The square of the "norm" of the Waldman Trubenbacher polynomial used in the state-to-state approximation
    """
    return molecule.avg_rot_energy_sq(T, False) - (molecule.avg_rot_energy(T, False) ** 2)


def wt_poly_norm_multiT(T: float, T1: float, molecule: MoleculeMultiT, F: float=0.0) -> float:
    """Calculates the square of the "norm" of the Waldman Trubenbacher polynomial of the following form:
    :math:`P_{ij} = -[\\varepsilon_{ij} / kT - i F]'`, where the :math:`i` is the vibrational level of the molecule,
    :math:`j` is the rotational level of the molecule, :math:`[A]' = A - <A>_{int}`, where :math:`<>_{int}`
    denotes averaging over the internal spectrum.
    The square of the "norm" is defined as: :math:`||P_{ij}||^{2} = \\left<P_{ij}^{2} \\right>_{int}`

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule for which the polynomial is calculated
    molecule : MoleculeMultiT
        the molecule for which the polynomial is calculated
    F : float
        the constant appearing in the expression for the polynomial, defaults to ``0.0``

    Returns
    -------
    float
        The square of the "norm" of the Waldman Trubenbacher polynomial
    """
    return molecule.avg_vibr_energy_sq(T, T1, False) + molecule.avg_rot_energy_sq(T, False)\
                                                     + molecule.avg_i_sq(T, T1) * (F ** 2)\
                                                     + 2 * molecule.avg_vibr_energy(T, T1, False)\
                                                         * molecule.avg_rot_energy(T, False)\
                                                     - 2 * molecule.avg_vibr_energy_i(T, T1, False) * F\
                                                     - 2 * molecule.avg_rot_energy(T, False) * molecule.avg_i(T, T1)\
                                                                                             * F\
                                                     - (wt_simple_avg(T, T1, molecule, F) ** 2)


def wt_poly_norm_oneT(T: float, molecule: MoleculeOneT) -> float:
    """Calculates the square of the "norm" of the Waldman Trubenbacher polynomial of the following form:
    :math:`P_{ij} = -[\\varepsilon_{ij} / kT]'`, where the :math:`i` is the vibrational level of the molecule,
    :math:`j` is the rotational level of the molecule, :math:`[A]' = A - <A>_{int}`, where :math:`<>_{int}`
    denotes averaging over the internal spectrum.
    The square of the "norm" is defined as: :math:`||P_{ij}||^{2} = \\left<P_{ij}^{2} \\right>_{int}`

    Parameters
    ----------
    T : float
        the temperature of the mixture
    molecule : MoleculeOneT
        the molecule for which the polynomial is calculated
    F : float
        the constant appearing in the expression for the polynomial, defaults to ``0.0``

    Returns
    -------
    float
        The square of the "norm" of the Waldman Trubenbacher polynomial
    """
    return molecule.avg_vibr_energy_sq(T, False) - (molecule.avg_vibr_energy(T, False) ** 2)\
           + molecule.avg_rot_energy_sq(T, False) - (molecule.avg_rot_energy(T, False) ** 2)


def wt_simple_avg(T: float, T1: float, molecule: MoleculeMultiT, F: float=0.0) -> float:
    """Calculates the averaging over the internal energy spectrum of the following expression:
    :math:`\\varepsilon_{ij} / kT - i F`;
    that is, the quantity :math:`\\left<\\varepsilon_{ij} / kT - i F\\right>_{int}`

    Parameters
    ----------
    T : float
        the temperature of the mixture
    T1 : float
        the temperature of the first vibrational level of the molecule for which the polynomial is calculated
    molecule : MoleculeMultiT
        the molecule for which the polynomial is calculated
    F : float
        the constant appearing in the expression for the polynomial, defaults to ``0.0``

    Returns
    -------
    float
        The averaging over the internal energy spectrum Waldman Trubenbacher polynomial
    """
    return molecule.avg_full_energy(T, T1, False) - molecule.avg_i(T, T1) * F