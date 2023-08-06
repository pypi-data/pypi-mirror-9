"""Contains all particle classes: the base Particle class, the Atom, MoleculeSTS (State-To-State) and Molecule classes
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"

import numpy as np
from scipy import constants
from os.path import normcase, join, split
from math import exp


class Particle(object):
    """The base Particle class, serving as the basis for the Atom and MoleculeSTS classes

    Attributes
    ----------
    name : str
        The name of the particle
    mass : float
        The mass of the particle
    LJe : float
        The particle Lennard-Jones :math:`\\varepsilon` parameter (stored as :math:`\\varepsilon / k`)
    LJs : float
        The particle Lennard-Jones :math:`\\sigma` parameter (the particle radius)
    form : float
        The formation energy of the particle

    """
    def __init__(self, name: str, mass: float, LJe: float, LJs: float, form: float):
        """Creates a new particle

        Parameters
        ----------
        name : str
            The name of the particle
        mass : float
            The mass of the particle
        LJe : float
            The particle Lennard-Jones :math:`\\varepsilon` parameter (stored as :math:`\\varepsilon / k`)
        LJs : float
            The particle Lennard-Jones :math:`\\sigma` parameter (the particle radius)
        form : float
            The formation energy of the particle
        """
        self.name = name
        self.mass = mass
        self.LJe = LJe
        self.LJs = LJs
        self.form = form


class Atom(Particle):
    """The Atom class

    Attributes
    ----------
    name : str
        The name of the particle
    mass : float
        The mass of the particle
    LJe : float
        The particle Lennard-Jones :math:`\\varepsilon` parameter (stored as :math:`\\varepsilon / k`)
    LJs : float
        The particle Lennard-Jones :math:`\\sigma` parameter (the particle radius)
    form : float
        The formation energy of the particle

    """
    def __init__(self, name: str, mass=None, LJe=None, LJs=None, form=None):
        """Creates a new atom

        Parameters
        ----------
        name : str
            The name of the atom
        mass : float
            The mass of the particle (in kilograms), if one wants to use a mass different from the data included with
            the library, if equal to None, the data included with the library is used, defaults to None
        LJe : float
            The particle Lennard-Jones :math:`\\varepsilon` parameter, divided by Boltzmann's constant,
            if one wants to use a math:`\\varepsilon` parameter different from the data included with
            the library, if equal to None, the data included with the library is used, defaults to None
        LJs : float
            The particle Lennard-Jones :math:`\\sigma` parameter (in meters), if one wants to use a Lennard-Jones
            :math:`\\sigma` parameter different from the data included with
            the library, if equal to None, the data included with the library is used, defaults to None
        form : float
            The formation energy of the particle (in Joules), if one wants to use a formation energy
            different from the data included with the library, if equal to None, the data included with the library
            is used, defaults to None
        """
        file_opened = False
        if mass is None:
            if not file_opened:
                this_dir, this_filename = split(__file__)
                raw_d = np.genfromtxt(join(this_dir, normcase('data/particles/' + name + '.dat')))
                file_opened = True
            mass = raw_d[0] * constants.physical_constants['atomic mass constant'][0]
        if LJe is None:
            if not file_opened:
                this_dir, this_filename = split(__file__)
                raw_d = np.genfromtxt(join(this_dir, normcase('data/particles/' + name + '.dat')))
                file_opened = True
            LJe = raw_d[1]
        if LJs is None:
            if not file_opened:
                this_dir, this_filename = split(__file__)
                raw_d = np.genfromtxt(join(this_dir, normcase('data/particles/' + name + '.dat')))
                file_opened = True
            LJs = raw_d[2] * constants.physical_constants['Angstrom star'][0]
        if form is None:
            if not file_opened:
                this_dir, this_filename = split(__file__)
                raw_d = np.genfromtxt(join(this_dir, normcase('data/particles/' + name + '.dat')))
            form = 0.5 * raw_d[3] * constants.physical_constants['electron volt'][0]
        Particle.__init__(self, name, mass, LJe, LJs, form)


class Molecule(Particle):
    """Molecule class for a state-to-state approximation
    Provides various methods such as averaged rotational energies, rotational exponents,
    dissociation-related partition functions, etc.

    Attributes
    ----------
    name : str
        The name of the particle
    mass : float
        The mass of the particle
    LJe : float
        The particle Lennard-Jones :math:`\\varepsilon` parameter (stored as :math:`\\varepsilon / k`)
    LJs : float
        The particle Lennard-Jones :math:`\\sigma` parameter (the particle radius)
    form : float
        The formation energy of the particle
    vibr_model : str
        The model of the vibrational spectrum (can be either 'harmonic', 'anharmonic' or 'table', if pre-calculated
        table values are used for each vibrational level)
    rot_symmetry : float
        The rotational symmetry factor (equal to 2.0 if the molecule is homonuclear and to 1.0 otherwise)
    num_rot : int
        The number of rotational levels in the molecule
    num_vibr : int
        The number of vibrational levels in the molecule
    inertia : float
        The moment of rotational inertia :math:`I_{rot,c}`
    rot_const : float
        The quantity :math:`h ^ 2 / (8 \\pi ^ 2 I_{rot,c})`, where :math:`I_{rot,c}` is the moment of rotational
        inertia
    hvc : float
        The harmonic coefficient in the formula for vibrational level energies
    avc : float
        The anharmonic coefficient in the formula for vibrational level energies
    diss : float
        The dissociation energy of the molecule
    rot : ndarray
        The array of rotational energies for each level
    vibr : ndarray
        The array of vibrational energies for each level
    vibr_zero : float
        The energy of the 0th vibrational level (stored separately as the value of the energy of
        the 0th vibrational level in the ``vibr`` array is equal to 0)
    crot : float
        The specific heat capacity of rotational degrees of freedom
    infcoll : float
        The Parker's limiting value for the molecular species

    Notes
    -----
    Attributes whose names begin with `_current_` are not meant to be accessed directly, as doing so may lead to errors,
    they are calculated when the `renorm_sts` method is called, and are correct only if the current flow temperature
    is the same as the temperature which was passed to the `renorm_sts` method.
    """
    def __init__(self, name: str, vmodel: str='anharmonic'):
        """Creates a new molecule

        Parameters
        ----------
        name : str
            The name of the molecule ('N2', 'NO', etc.)
        vmodel : str
            The model to be used for the vibrational spectrum, possible values:
                * 'harmonic'
                * 'anharmonic'
                * 'table' (if 'table' is used and no file containing the energy values is found, the
                  'anharmonic' model will be used)

            defaults to 'anharmonic'
        """
        self.vibr_model = vmodel
        this_dir, this_filename = split(__file__)
        raw_d = np.genfromtxt(join(this_dir, normcase('data/particles/' + name + '.dat')))
        mass = raw_d[0] * constants.physical_constants['atomic mass constant'][0]
        self.num_rot = int(raw_d[1])
        self.rot_symmetry = raw_d[2]
        if vmodel == 'harmonic':
            self.num_vibr = int(raw_d[3])
        elif vmodel == 'anharmonic' or vmodel == 'table':
            self.num_vibr = int(raw_d[4])
        self.inertia = raw_d[5] * (10 ** (-46))
        self.rot_const = (constants.h ** 2) / (8.0 * (constants.pi ** 2) * self.inertia)
        self.hvc = raw_d[6] * 100 * constants.h * constants.c
        self.avc = raw_d[7]
        self.diss = raw_d[8] * constants.physical_constants['electron volt'][0]
        form = raw_d[9] * constants.physical_constants['electron volt'][0]
        LJe = raw_d[10]  # stored as eps/kboltz
        LJs = raw_d[11] * constants.physical_constants['Angstrom star'][0]
        Particle.__init__(self, name, mass, LJe, LJs, form)
        self.rot = np.zeros(self.num_rot + 1)
        self.vibr = np.zeros(self.num_vibr + 1)
        self.vibr_zero = 0
        self.crot = constants.k / self.mass
        self.infcoll = raw_d[12]

        self._current_T = 1.0
        self._current_Z_rot = 0.0
        self._current_rae = 0.0
        self._current_raesq = 0.0
        self._current_kT = 1.0

        a = np.arange(0, self.num_vibr + 1, 1)
        if self.vibr_model == 'table':
            try:
                f = open(normcase('data/spectra/' + self.name + '.dat'))
                f.close()
                raw_v_d = np.genfromtxt(normcase('data/spectra/' + self.name + '.dat'))
                self.vibr_zero = self.vibr[0]
                self.vibr = raw_v_d * constants.physical_constants['electron volt'][0]
                self.vibr = self.vibr - self.vibr[0]
                self.num_vibr = self.vibr.shape[0]
            except IOError:
                print('File with vibrational energies not found, will use anharmonic oscillator model')
                self.vibr_model = 'anharmonic'
                self.vibr_zero = 0.5 * self.hvc * (1 - 0.5 * self.avc)
                self.vibr = self.hvc * (1.0 - self.avc) * a - self.hvc * self.avc * (a ** 2)

        elif self.vibr_model == 'anharmonic':
            self.vibr_zero = 0.5 * self.hvc * (1 - 0.5 * self.avc)
            self.vibr = self.hvc * (1.0 - self.avc) * a - self.hvc * self.avc * (a ** 2)
        elif self.vibr_model == 'harmonic':
            self.vibr_zero = 0.5 * self.hvc
            self.vibr = self.hvc * a

        for j in range(self.num_rot + 1):
            self.rot[j] = j * (j + 1) * self.rot_const
        self.vibr += self.vibr_zero

    def renorm_sts(self, T: float):
        """Calculates all _current values for the molecule

        Parameters
        ----------
        T : float
            the temperature of the mixture
        """
        self._current_Z_rot = self.Z_rot(T)
        self._current_rae = self.avg_rot_energy(T, True)
        self._current_raesq = self.avg_rot_energy_sq(T, True)
        self._current_T = T
        self._current_kT = constants.k * T

    def vibr_energy(self, i):
        """Returns the energy of the ``i``-th vibrational level :math:`\\varepsilon_{i}`

        Parameters
        ----------
        i : int or 1-D array-like
            the number of the level (or a an array/list of level numbers) for which to return the vibrational energy

        Returns
        -------
        float or 1-D array-like
            The energy of the i-th vibrational level, or, if the input the ``i`` parameter is array-like, an array of
            vibrational energies
        """
        return self.vibr[i]

    def rot_energy(self, j):
        """Returns the energy of the ``j``-th rotational level :math:`\\varepsilon_{j}`

        Parameters
        ----------
        j : int or float
            the number of the level for which to return the rotational energy

        Returns
        -------
        float or 1-D array-like
            The energy of the ``j``-th rotational level, (`float` values of ``j`` are used for integration)
        """
        if (int(j) - j) == 0 and j <= self.num_rot:
            return self.rot[j]
        else:  # non-integer values are used for integration
            return j * (j + 1) * self.rot_const

    def full_energy(self, i, j):
        """Returns the sum of the energy of the ``j``-th rotational level and the energy of the ``i``-th vibrational
        level (the total energy of the `ij`-th rotovibrational state) :math:`\\varepsilon_{ij}`

        Parameters
        ----------
        i : int or 1-D array-like
            the number of the level (or a an array/list of level numbers) for which to return the vibrational energy
        j : int or 1-D array-like
            the number of the level (or a an array/list of level numbers) for which to return the rotational energy

        Returns
        -------
        float or 1-D array-like
            The total energy of the `ij`-th rotovibrational state

        Notes
        -----
        The dimensions of ``i`` and ``j`` must match
        """
        return self.vibr[i] + self.rot[j]

    def rot_exp(self, T: float, j):
        """Returns the rotational exponent: :math:`((2j + 1) / \\sigma_{rot}) exp(-\\varepsilon_{j} / kT)`,
        :math:`(2j + 1)`
        being the degeneracy of the j-th rotational state, and :math:`\\sigma_{rot}` being the rotational symmetry
        factor

        Parameters
        ----------
        j : int or float
            the number of the level for which to return the rotational exponent
        T : float
            the temperature of the mixture

        Returns
        -------
        float or 1-D np.ndarray
            The rotational exponent for a given index ``j``
        """
        return ((2.0 * j + 1.0) / self.rot_symmetry) * exp(-self.rot_energy(j) / (constants.k * T))

    def Z_rot(self, T: float) -> float:
        """Returns the rotational partition function :math:`Z_{rot}(T)`

        Parameters
        ----------
        T : float
            the temperature of the mixture

        Returns
        -------
        float
            The rotational partition function
        """
        if self._current_T != T:
            return 8.0 * (constants.pi ** 2) * self.inertia * constants.k * T / (self.rot_symmetry * (constants.h ** 2))
        else:
            return self._current_Z_rot

    def avg_rot_energy(self, T: float, dimensional: bool=True) -> float:
        """Returns the rotational energy averaged over the rotational spectrum (either dimensional
        :math:`\\left<\\varepsilon^{rot} \\right>_{rot}` or dimensionless
        :math:`\\left<\\varepsilon^{rot} / kT \\right>_{rot}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        dimensional : bool
            if True, the dimensional averaged rotational energy is returned, if False, the dimensionless averaged
            rotational energy is returned, defaults to True

        Returns
        -------
        float
            The averaged rotational energy
        """
        if self._current_T != T:
            kT = constants.k * T
            B = self.rot_const / kT
            snr = self.num_rot * (self.num_rot + 1.0)

            if dimensional:
                return kT * (1.0 + exp(-B * snr) * (-B * snr - 1.0)) / (self.rot_symmetry * self.Z_rot(T) * B)
            else:
                return (1.0 + exp(-B * snr) * (-B * snr - 1.0)) / (self.rot_symmetry * self.Z_rot(T) * B)
        else:
            if dimensional:
                return self._current_rae
            else:
                return self._current_rae / self._current_kT

    def avg_rot_energy_sq(self, T: float, dimensional: bool=True) -> float:
        """
        Returns the squared rotational energy averaged over the rotational spectrum (either dimensional
        :math:`\\left<\\left(\\varepsilon^{rot}\\right)^{2}\\right>_{rot}`
        or dimensionless :math:`\\left<\\left(\\varepsilon^{rot}/kT\\right)^{2}\\right>_{rot}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        dimensional : bool
            if True, the averaged squared dimensional rotational energy is returned, if False, the averaged squared
            dimensionless rotational energy is returned, defaults to True

        Returns
        -------
        float
            The averaged squared rotational energy
        """
        if self._current_T != T:
            kT = constants.k * T
            B = self.rot_const / kT
            snr = self.num_rot * (self.num_rot + 1)
            if dimensional:
                return (2.0 + exp(-B * snr) * (-B * snr * (B * snr + 2) - 2)) * (kT ** 2) / (self.rot_symmetry
                                                                                             * self.Z_rot(T) * B)
            else:
                return (2.0 + exp(-B * snr) * (-B * snr * (B * snr + 2) - 2)) / (self.rot_symmetry
                                                                                 * self.Z_rot(T) * B)
        else:
            if dimensional:
                return self._current_raesq
            else:
                return self._current_raesq / (self._current_kT ** 2)

    def Z_vibr_eq(self, T: float, model: str='none') -> float:
        """Returns the equilibrium vibrational partition function :math:`Z_{eq}(T)` (which is used in various
        dissociation models) as a function of either the temperature T or the parameter U (specified by ``model``).
        If U is equal to 0,
        the result is just the equilibirum vibrational partition function (except that the the vibrational energy
        at the zero level is not equal to zero); otherwise, the parameter U is used instead of the temperature T

        Parameters
        ----------
        T : float
            the temperature of the mixture
        model : str
            the model for the parameter `U` to be used, possible values:
                * 'none' - the temperature T will be used and the method will return the equilibrium vibrational
                  partition function
                * 'inf' - the method will return `Z_vibr_eq(-infinity, 0)`
                * 'D6k' - the method will return `Z_vibr_eq(-D / 6k, 0)` (where `D` is the dissociation energy of
                  the molecule)
                * '3T' - the method will return `Z_vibr_eq(-3T, 0)`

            defaults to 'none'

        Returns
        -------
        float
            The equilibrium vibrational partition function (either as a function of T or as a function of U)
        """

        if model == 'none':
            return np.sum(np.exp(-(self.vibr_zero + self.vibr) / (T * constants.k)))
        elif model == 'inf':
            return self.num_vibr + 1.0
        elif model == 'D6k':
            return np.sum(np.exp(6.0 * ((self.vibr + self.vibr_zero) / self.diss)))
        elif model == '3T':
            return np.sum(np.exp((self.vibr_zero + self.vibr) / (3.0 * constants.k * T)))

    def Z_diss(self, T: float, i, model: str='D6k'):
        """Returns the non-equilibrium factor (which is used in various
        dissociation models) as a function of the temperature T and a parameter U (specified by ``model``) and
        the vibrational level ``i``, which is equal to
        :math:`Z_{eq}(T) \\exp(\\varepsilon_{i} (1 / T + 1 / U) / k) / Z_{eq}(-U)`

        Parameters
        ----------
        i : int or 1-D array-like
            the number of the level (or a an array/list of level numbers) for which to return the non-equilibrium factor
        T : float
            the temperature of the mixture
        model : str
            the model for the parameter `U` to be used, possible values:
                * 'inf' - the method will use `Z_vibr_eq(-infinity, 0)`
                * 'D6k' - the method will use `Z_vibr_eq(-D / 6k, 0)` (where `D` is the dissociation energy of
                  the molecule)
                * '3T' - the method will use `Z_vibr_eq(-3T, 0)`

            defaults to 'D6k'

        Returns
        -------
        float
            The non-equilibrium factor
        """
        if model == 'inf':
            return exp((self.vibr[i] + self.vibr_zero) / (T * constants.k))\
                   * self.Z_vibr_eq(T, 'none') / self.Z_vibr_eq(T, model)
        elif model == 'D6k':
            return exp((self.vibr[i] + self.vibr_zero) * (1.0 / (constants.k * T) + 6.0 / self.diss))\
                   * self.Z_vibr_eq(T, 'none') / self.Z_vibr_eq(T, model)
        elif model == '3T':
            return exp((self.vibr[i] + self.vibr_zero) / (0.75 * T * constants.k))\
                   * self.Z_vibr_eq(T, 'none') / self.Z_vibr_eq(T, model)


class MoleculeQuasi(Molecule):
    """Molecule class for quasi-stationary approximations
    Used for type annotations, adds some internal things compared to the Molecule class, but other than that,
    is fully identical.
    """
    def __init__(self, name, vmodel='anharmonic'):
        """Creates a new molecule

        Parameters
        ----------
        name : str
            The name of the molecule ('N2', 'NO', etc.)
        vmodel : str
            The model to be used for the vibrational spectrum, possible values:
                * 'harmonic'
                * 'anharmonic'
                * 'table' (if 'table' is used and no file containing the energy values is found, the
                  'anharmonic' model will be used)

            defaults to 'anharmonic'
        """
        Molecule.__init__(self, name, vmodel)

        self._current_Z_vibr = 0.0
        self._current_n = 0.0
        self._current_ni = np.zeros(self.num_vibr + 1)
        self._current_v_exp = np.zeros(self.num_vibr + 1)
        self._current_edt = 0.0
        self._current_zdt = 0.0
        self._current_vae = 0.0
        self._current_vaesq = 0.0
        self._current_edt = 0.0

        self._current_kT = 0.0


class MoleculeMultiT(MoleculeQuasi):
    """Molecule class for a multi-temperature approximation
    Provides additional methods (compared to ``Molecule``) such as averaged vibrational energies, vibrational exponents,
    etc.

    Attributes
    ----------
    See ``Molecule`` class

    Notes
    -----
    Attributes whose names begin with `_current_` are not meant to be accessed directly, as doing so may lead to errors,
    they are calculated when the `renorm` method is called, and are correct only if the current flow temperature
    is the same as the temperature which was passed to the `renorm` method.

    The energy of the 0th vibrational level is set to 0, the non-zero value is stored in the vibr_zero field
    """
    def __init__(self, name, vmodel='anharmonic'):
        """Creates a new molecule

        Parameters
        ----------
        name : str
            The name of the molecule ('N2', 'NO', etc.)
        vmodel : str
            The model to be used for the vibrational spectrum, possible values:
                * 'harmonic'
                * 'anharmonic'
                * 'table' (if 'table' is used and no file containing the energy values is found, the
                  'anharmonic' model will be used)

            defaults to 'anharmonic'
        """
        MoleculeQuasi.__init__(self, name, vmodel)

        self.max_vibr = self.num_vibr
        self._current_T1 = 1.0
        self._current_Z_vibr = 0.0
        self._current_Z_int = 0.0
        self._current_n = 0.0
        self._current_ni = np.zeros(self.num_vibr + 1)
        self._current_v_exp = np.zeros(self.num_vibr + 1)
        self._current_avg_i = 0.0
        self._current_avg_i_sq = 0.0
        self._current_wdt = 0.0
        self._current_wdt1 = 0.0
        self._current_edt1 = 0.0
        self._current_zdt = 0.0
        self._current_zdt1 = 0.0
        self._current_vae = 0.0
        self._current_vaesq = 0.0
        self._current_vae_i = 0.0
        self.vibr -= self.vibr_zero

    def renorm(self, T: float, T1: float, n_c: float):
        """Calculates all _current values for the molecule

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species
        n_c : float
            the numeric density of the molecular species
        """
        self.num_vibr = self.num_vibr_levels(T, T1, True)

        self._current_Z_rot = self.Z_rot(T)
        self._current_rae = self.avg_rot_energy(T, True)
        self._current_raesq = self.avg_rot_energy_sq(T, True)

        self._current_Z_vibr = self.Z_vibr(T, T1)
        self._current_Z_int = self.Z_int(T, T1)
        self._current_vae = self.avg_vibr_energy(T, T1, True)
        self._current_vaesq = self.avg_vibr_energy_sq(T, T1, True)
        self._current_avg_i = self.avg_i(T, T1)
        self._current_avg_i_sq = self.avg_i_sq(T, T1)
        self._current_wdt = self.W_dT(T, T1)
        self._current_wdt1 = self.W_dT1(T, T1)
        self._current_edt = self.E_vibr_dT(T, T1)
        self._current_edt1 = self.E_vibr_dT1(T, T1)
        self._current_zdt = self.Z_vibr_dT(T, T1)
        self._current_zdt1 = self.Z_vibr_dT1(T, T1)
        self._current_vae_i = self.avg_vibr_energy_i(T, T1, True)

        a = np.arange(0, self.num_vibr + 1, 1)
        self._current_v_exp = self.vibr_exp(T, T1, a)
        self._current_ni = self.ni(T, T1, a, n_c)
        self._current_n = n_c
        self._current_T1 = T1
        self._current_T = T
        self._current_kT = constants.k * T

    def num_vibr_levels(self, T: float, T1: float, true_amt: bool=True) -> int:
        """Returns the amount of vibrational levels (either the maximum one or current one)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species
        true_amt : bool
            if True, the true amount of vibrational levels is returned (which may be smaller than the maximum one if
            T < T1), if False, the maximum amount of vibrational levels is returned, defaults to True

        Returns
        -------
        int
            The amount of vibrational levels
        """
        if not true_amt:
            return self.max_vibr
        else:
            if (self._current_T != T) or (self._current_T1 != T1):
                if T < T1:
                    if self.avc == 0.0:
                        treanor_i_star = self.num_vibr
                    else:
                        treanor_i_star = int(0.5 + self.vibr[1] * T / (2 * self.avc * self.hvc * T1))
                else:
                    treanor_i_star = int(0.5 + self.vibr[1] * T / (2 * self.avc * self.hvc * T1))
                if self.max_vibr > treanor_i_star:
                    return treanor_i_star
                else:
                    return self.max_vibr
            else:
                return self.num_vibr

    def vibr_exp(self, T: float, T1: float, i):
        """Returns the vibrational exponent: :math:`\\exp((-\\varepsilon_{i} - i \\varepsilon_{1}) / kT
        - i \\varepsilon_{1} / kT_{1})`

        Parameters
        ----------
        i : int or 1-D array-like
            the number of the level (or a an array/list of level numbers) for which to return the vibrational exponent
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float or 1-D np.ndarray
            The vibrational exponent for a given index or set of indices `i`
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            return np.exp(-(self.vibr[i] - i * self.vibr[1]) / (T * constants.k)
                          - i * self.vibr[1] / (T1 * constants.k))
        else:
            return self._current_v_exp[i]

    def Z_vibr(self, T: float, T1: float) -> float:
        """Returns the vibrational partition function :math:`Z_{vibr}(T, T_{1})`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The vibrational partition function
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            return self.vibr_exp(T, T1, np.arange(0, self.num_vibr_levels(T, T1, True) + 1, 1)).sum()
        else:
            return self._current_Z_vibr

    def Z_int(self, T: float, T1: float) -> float:
        """Returns the internal partition function :math:`Z_{int}(T, T_{1}) = Z_{rot}(T) Z_{vibr}(T, T_{1})`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The vibrational partition function
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            return self.Z_rot(T) * self.Z_vibr(T, T1)
        else:
            return self._current_Z_int

    def avg_vibr_energy(self, T: float, T1: float, dimensional: bool=True) -> float:
        """Returns the vibrational energy averaged over the vibrational spectrum (either dimensional
        :math:`\\left<\\varepsilon^{vibr} \\right>_{vibr}` or dimensionless
        :math:`\\left<\\varepsilon^{vibr} / kT \\right>_{vibr}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species
        dimensional : bool
            if True, the dimensional averaged vibrational energy is returned, if False, the dimensionless averaged
            vibrational energy is returned, defaults to True

        Returns
        -------
        float
            The averaged vibrational energy
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            a = np.arange(0, self.num_vibr_levels(T, T1, True) + 1, 1)
            if dimensional:
                return np.dot(self.vibr_exp(T, T1, a), self.vibr[a]) / self.Z_vibr(T, T1)
            else:
                return np.dot(self.vibr_exp(T, T1, a), self.vibr[a] / (constants.k * T)) / self.Z_vibr(T, T1)
        else:
            if dimensional:
                return self._current_vae
            else:
                return self._current_vae / self._current_kT

    def avg_full_energy(self, T: float, T1: float, dimensional: bool=True) -> float:
        """Returns the full internal energy averaged over the internal spectrum (either dimensional
        :math:`\\left<\\varepsilon^{int} \\right>_{int}` or dimensionless
        :math:`\\left<\\varepsilon^{int} / kT \\right>_{int}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species
        dimensional : bool
            if True, the dimensional averaged internall energy is returned, if False, the dimensionless averaged
            internal energy is returned, defaults to True

        Returns
        -------
        float
            The averaged internal energy
        """
        return self.avg_vibr_energy(T, T1, dimensional) + self.avg_rot_energy(T, dimensional)

    def avg_vibr_energy_sq(self, T: float, T1: float, dimensional: bool=True) -> float:
        """Returns the squared vibrational energy averaged over the vibrational spectrum (either dimensional
        :math:`\\left<\\left(\\varepsilon^{vibr} \\right)^{2}\\right>_{vibr}`
        or dimensionless :math:`\\left<\\left(\\varepsilon^{vibr} / kT \\right)^{2}\\right>_{vibr}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species
        dimensional : bool
            if True, the averaged squared dimensional vibrational energy is returned, if False, the averaged squared
            dimensionless vibrational energy is returned, defaults to True

        Returns
        -------
        float
            The averaged squared vibrational energy
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            a = np.arange(0, self.num_vibr_levels(T, T1, True) + 1, 1)
            if dimensional:
                return np.dot(self.vibr_exp(T, T1, a), np.power(self.vibr[a], 2)) / self.Z_vibr(T, T1)
            else:
                return np.dot(self.vibr_exp(T, T1, a), np.power(self.vibr[a] / (constants.k * T), 2))\
                       / self.Z_vibr(T, T1)
        else:
            if dimensional:
                return self._current_vaesq
            else:
                return self._current_vaesq / (self._current_kT ** 2)

    def avg_i(self, T: float, T1: float) -> float:
        """Returns the average amount of vibrational quanta :math:`<i>_{vibr}`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The average amount of vibrational quanta
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            a = np.arange(0, self.num_vibr_levels(T, T1, True) + 1, 1)
            res = np.dot(self.vibr_exp(T, T1, a), a)
            return res / self.Z_vibr(T, T1)
        else:
            return self._current_avg_i

    def avg_i_sq(self, T: float, T1: float) -> float:
        """Returns the squared vibrational energy level, averaged over the vibrational spectrum
        :math:`<i^{2}>_{vibr}`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The averaged squared vibrational level
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            a = np.arange(0, self.num_vibr_levels(T, T1, True) + 1, 1)
            res = np.dot(self.vibr_exp(T, T1, a), np.power(a, 2))
            return res / self.Z_vibr(T, T1)
        else:
            return self._current_avg_i_sq

    def avg_vibr_energy_i(self, T: float, T1: float, dimensional: bool=True) -> float:
        """Returns the energy level multiplied by the corresponding vibrational energy, averaged over the vibrational
        spectrum (either dimensional :math:`\\left<i\\varepsilon_{i} \\right>_{vibr}` or dimensionless
        :math:`\\left<i\\varepsilon_{i} / kT \\right>_{vibr}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species
        dimensional : bool
            if True, the averaged dimensional vibrational energy multiplied by the corresponding level number
            is returned, if False, the averaged dimensionless vibrational energy by the corresponding level number is
            returned, defaults to True

        Returns
        -------
        float
            The averaged vibrational level multiplied by the corresponding vibrational energy
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            a = np.arange(0, self.num_vibr_levels(T, T1, True) + 1, 1)
            if dimensional:
                return np.dot(a * self.vibr[a], self.vibr_exp(T, T1, a)) / self.Z_vibr(T, T1)
            else:
                return np.dot(a * self.vibr[a] / (constants.k * T), self.vibr_exp(T, T1, a)) / self.Z_vibr(T, T1)
        else:
            if dimensional:
                return self._current_vae_i
            else:
                return self._current_vae_i / self._current_kT

    def ni(self, T: float, T1: float, i, n_c: float) -> float:
        """Returns the numeric density of the ``i``-th vibrational level :math:`n_{i}` for the molecular species

        Parameters
        ----------
        i : int or 1-D array-like
            the number of the level (or a an array/list of level numbers) for which to return the numeric densities
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species
        n_c : float
            the numeric density of the molecular species

        Returns
        -------
        float or 1-D np.ndarray
            The numeric density for a given index or set of indices `i`
        """
        if (self._current_T != T) or (self._current_T1 != T1) or (self._current_n != n_c):
            return n_c * self.vibr_exp(T, T1, i) / self.Z_vibr(T, T1)
        else:
            return self._current_ni[i]

    def Z_vibr_dT(self, T: float, T1: float) -> float:
        """Returns the partial derivative of the vibrational partition function :math:`Z_{vibr}` with respect to the
        temperature :math:`T`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The partial derivative of the vibrational partition function with respect to the temperature :math:`T`
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            a = np.arange(0, self.num_vibr_levels(T, T1, True) + 1, 1)
            return np.dot(self.vibr[a] - a * self.vibr[1], self.vibr_exp(T, T1, a)) / (constants.k * T * T)
        else:
            return self._current_zdt

    def Z_vibr_dT1(self, T: float, T1: float) -> float:
        """Returns the partial derivative of the vibrational partition function :math:`Z_{vibr}` with respect to the
        temperature of the first vibrational level :math:`T_{1}`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The partial derivative of the vibrational partition function with respect to the temperature of
            the first vibrational level :math:`T_{1}`
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            a = np.arange(0, self.num_vibr_levels(T, T1, True) + 1, 1)
            return self.vibr[1] * np.dot(a, self.vibr_exp(T, T1, a)) / (constants.k * T1 * T1)
        else:
            return self._current_zdt1

    def W_dT(self, T: float, T1: float) -> float:
        """Returns the partial derivative of the average number of vibrational quanta per unit mass :math:`W` with
        respect to the temperature :math:`T`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The partial derivative of the average number of vibrational quanta per unit mass with respect to
            the temperature :math:`T`
        """
        if self.vibr_model == 'harmonic':
                return 0.0
        else:
            if (self._current_T != T) or (self._current_T1 != T1):
                return (self.avg_vibr_energy_i(T, T1) - self.vibr[1] * self.avg_i_sq(T, T1)
                        - self.avg_i(T, T1) * self.avg_vibr_energy(T, T1) + self.vibr[1] * (self.avg_i(T, T1) ** 2))\
                        / (constants.k * T * T * self.mass)
            else:
                return self._current_wdt

    def W_dT1(self, T: float, T1: float) -> float:
        """Returns the partial derivative of the average number of vibrational quantaper unit mass :math:`W` with
        respect to the temperature of the first vibrational level :math:`T_{1}`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The partial derivative of the average number of vibrational quanta per unit mass with respect to
            the temperature of the first vibrational level :math:`T_{1}`
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            return self.vibr[1] * (self.avg_i_sq(T, T1) - (self.avg_i(T, T1) ** 2))\
                   / (constants.k * T1 * T1 * self.mass)
        else:
            return self._current_wdt1

    def E_vibr(self, T: float, T1: float) -> float:
        """Returns the full vibrational energy per unit mass :math:`E_{vibr}` (which is equal to the averaged
        vibrational energy divided by the molecule mass)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The full vibrational energy per unit mass
        """
        return self.avg_vibr_energy(T, T1) / self.mass

    def E_vibr_dT(self, T: float, T1: float) -> float:
        """Returns the partial derivative of the full vibrational energy per unit mass :math:`E_{vibr}` with respect
        to the temperature :math:`T`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The partial derivative of the full vibrational energy per unit mass with respect to the temperature
            :math:`T`
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            if self.vibr_model == 'harmonic':
                return 0.0
            else:
                return (self.avg_vibr_energy_sq(T, T1) - (self.avg_vibr_energy(T, T1) ** 2)
                        + self.vibr[1] * (self.avg_i(T, T1) * self.avg_vibr_energy(T, T1)
                                          - self.avg_vibr_energy_i(T, T1))) / (constants.k * T * T * self.mass)
        else:
            return self._current_edt

    def E_vibr_dT1(self, T: float, T1: float) -> float:
        """Returns the partial derivative of the full vibrational energy per unit mass :math:`E_{vibr}` with respect
        to the temperature of the first vibrational level :math:`T_{1}`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        T1 : float
            the temperature of the first vibrational level of the molecular species

        Returns
        -------
        float
            The partial derivative of the full vibrational energy per unit mass with respect to the temperature
            of the first vibrational level :math:`T_{1}`
        """
        if (self._current_T != T) or (self._current_T1 != T1):
            return (self.avg_vibr_energy_i(T, T1) - self.avg_i(T, T1) * self.avg_vibr_energy(T, T1))\
                    * self.vibr[1] / (constants.k * T1 * T1 * self.mass)
        else:
            return self._current_edt1


class MoleculeOneT(MoleculeQuasi):
    """Molecule class for a one-temperature approximation
    Provides additional methods (compared to ``Molecule``) such as averaged vibrational energies, vibrational exponents,
    etc.

    Attributes
    ----------
    See ``Molecule`` class

    Notes
    -----
    Attributes whose names begin with `_current_` are not meant to be accessed directly, as doing so may lead to errors,
    they are calculated when the `renorm` method is called, and are correct only if the current flow temperature
    is the same as the temperature which was passed to the `renorm` method.
    """
    def __init__(self, name, vmodel='anharmonic'):
        """Creates a new molecule

        Parameters
        ----------
        name : str
            The name of the molecule ('N2', 'NO', etc.)
        vmodel : str
            The model to be used for the vibrational spectrum, possible values:
                * 'harmonic'
                * 'anharmonic'
                * 'table' (if 'table' is used and no file containing the energy values is found, the
                  'anharmonic' model will be used)

            defaults to 'anharmonic'
        """
        MoleculeQuasi.__init__(self, name, vmodel)

    def renorm(self, T: float, n_c: float):
        """Calculates all _current values for the molecule

        Parameters
        ----------
        T : float
            the temperature of the mixture
        n_c : float
            the numeric density of the molecular species
        """
        self._current_Z_rot = self.Z_rot(T)
        self._current_rae = self.avg_rot_energy(T, True)
        self._current_raesq = self.avg_rot_energy_sq(T, True)

        self._current_Z_vibr = self.Z_vibr(T)
        self._current_vae = self.avg_vibr_energy(T, True)
        self._current_vaesq = self.avg_vibr_energy_sq(T, True)

        a = np.arange(0, self.num_vibr + 1, 1)
        self._current_v_exp = self.vibr_exp(T, a)
        self._current_ni = self.ni(T, a, n_c)
        self._current_n = n_c

        self._current_T = T
        self._current_kT = constants.k * T

    def vibr_exp(self, T: float, i):
        """Returns the vibrational exponent: :math:`\\exp(-\\varepsilon_{i} / kT)`

        Parameters
        ----------
        T : float
            the temperature of the mixture
        i : int or 1-D array-like
            the number of the level (or a an array/list of level numbers) for which to return the vibrational exponent
        zero_level : bool
            if ``True``, the energy of the vibrational energies are not counted from zero (and the energy of the 0-the
            vibrational level is not equal to zero), if ``False``,
            the energy of the vibrational energies are counted from zero (and the energy of the 0-th vibrational level
            is equal to zero), defaults to ``True``

        Returns
        -------
        float or 1-D np.ndarray
            The vibrational exponent for a given index or set of indices `i`
        """
        if self._current_T != T:
            return np.exp(-self.vibr[i] / (T * constants.k))
        else:
            return self._current_v_exp[i]

    def Z_vibr(self, T: float) -> float:
        """Returns the vibrational partition function :math:`Z_{vibr}(T)`

        Parameters
        ----------
        T : float
            the temperature of the mixture

        Returns
        -------
        float
            The vibrational partition function
        """
        if self._current_T != T:
            return self.vibr_exp(T, np.arange(0, self.num_vibr + 1, 1)).sum()
        else:
            return self._current_Z_vibr

    def Z_int(self, T: float) -> float:
        """Returns the internal partition function :math:`Z_{int}(T) = Z_{rot}(T) Z_{vibr}(T)`

        Parameters
        ----------
        T : float
            the temperature of the mixture

        Returns
        -------
        float
            The vibrational partition function
        """
        if self._current_T != T:
            return self.Z_rot(T) * self.Z_vibr(T)
        else:
            return self._current_Z_rot * self._current_Z_vibr

    def avg_vibr_energy(self, T: float, dimensional: bool=True) -> float:
        """Returns the vibrational energy averaged over the vibrational spectrum (either dimensional
        :math:`\\left<\\varepsilon^{vibr} \\right>_{vibr}` or dimensionless
        :math:`\\left<\\varepsilon^{vibr} / kT \\right>_{vibr}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        dimensional : bool
            if True, the dimensional averaged vibrational energy is returned, if False, the dimensionless averaged
            vibrational energy is returned, defaults to True

        Returns
        -------
        float
            The averaged vibrational energy
        """
        if self._current_T != T:
            a = np.arange(0, self.num_vibr + 1, 1)
            if dimensional:
                return np.dot(self.vibr_exp(T, a), self.vibr[a]) / self.Z_vibr(T)
            else:
                return np.dot(self.vibr_exp(T, a), self.vibr[a]
                              / (constants.k * T)) / self.Z_vibr(T)
        else:
            if dimensional:
                return self._current_vae
            else:
                return self._current_vae / self._current_kT

    def avg_full_energy(self, T: float, dimensional: bool=True) -> float:
        """Returns the full internal energy averaged over the internal spectrum (either dimensional
        :math:`\\left<\\varepsilon^{int} \\right>_{int}` or dimensionless
        :math:`\\left<\\varepsilon^{int} / kT \\right>_{int}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        dimensional : bool
            if True, the dimensional averaged internall energy is returned, if False, the dimensionless averaged
            internal energy is returned, defaults to True

        Returns
        -------
        float
            The averaged internal energy
        """
        return self.avg_vibr_energy(T, dimensional) + self.avg_rot_energy(T, dimensional)

    def avg_vibr_energy_sq(self, T: float, dimensional: bool=True) -> float:
        """Returns the squared vibrational energy averaged over the vibrational spectrum (either dimensional
        :math:`\\left<\\left(\\varepsilon^{vibr} \\right)^{2}\\right>_{vibr}`
        or dimensionless :math:`\\left<\\left(\\varepsilon^{vibr} / kT \\right)^{2}\\right>_{vibr}`)

        Parameters
        ----------
        T : float
            the temperature of the mixture
        dimensional : bool
            if True, the averaged squared dimensional vibrational energy is returned, if False, the averaged squared
            dimensionless vibrational energy is returned, defaults to True

        Returns
        -------
        float
            The averaged squared vibrational energy
        """
        if self._current_T != T:
            a = np.arange(0, self.num_vibr + 1, 1)
            if dimensional:
                return np.dot(self.vibr_exp(T, a), np.power(self.vibr[a], 2))\
                       / self.Z_vibr(T)
            else:
                return np.dot(self.vibr_exp(T, a), np.power(self.vibr[a]
                                                                  / (constants.k * T), 2)) / self.Z_vibr(T)
        else:
            if dimensional:
                return self._current_vaesq
            else:
                return self._current_vaesq / (self._current_kT ** 2)

    def ni(self, T: float, i, n_c: float):
        """Returns the numeric density of the ``i``-th vibrational level :math:`n_{i}` for the molecular species

        Parameters
        ----------
        T : float
            the temperature of the mixture
        i : int or 1-D array-like
            the number of the level (or a an array/list of level numbers) for which to return the numeric densities
        n_c : float
            the numeric density of the molecular species

        Returns
        -------
        float or 1-D np.ndarray
            The numeric density for a given index or set of indices `i`
        """
        if (self._current_T != T) or (self._current_n != n_c):
            return n_c * self.vibr_exp(T, i) / self.Z_vibr(T)
        else:
            return self._current_ni[i]

    def E_vibr(self, T: float) -> float:
        """Returns the full vibrational energy per unit mass :math:`E_{vibr}` (which is equal to the averaged
        vibrational energy divided by the molecule mass)

        Parameters
        ----------
        T : float
            the temperature of the mixture

        Returns
        -------
        float
            The full vibrational energy per unit mass
        """
        return self.avg_vibr_energy(T) / self.mass

    def E_vibr_dT(self, T: float) -> float:
        """Returns the partial derivative of the full vibrational energy per unit mass :math:`E_{vibr}` with respect
        to the temperature :math:`T`

        Parameters
        ----------
        T : float
            the temperature of the mixture

        Returns
        -------
        float
            The partial derivative of the full vibrational energy per unit mass with respect to the temperature
            :math:`T`
        """
        if self._current_T != T:
            return (self.avg_vibr_energy_sq(T) - self.avg_vibr_energy(T) ** 2) / (constants.k * T * T * self.mass)
        else:
            return self._current_edt