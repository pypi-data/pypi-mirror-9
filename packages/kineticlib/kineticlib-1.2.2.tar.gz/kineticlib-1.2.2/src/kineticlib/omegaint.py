"""Contains formulas for elastic omega integrals for various cross-section parameters
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Development"


import numpy as np
from scipy import constants
from math import gamma, exp
from scipy.misc import factorial
from .errors import KineticlibError


def omega(T: float, l: int, r: int, idata: np.ndarray, model: str='ESA', dimensional: bool=True,
          nokt: bool=False) -> float:
    """Returns the :math:`\\Omega^{(l,r)}`-integral for a specified potential

    Parameters
    ----------
    T : float
        the temperature of the mixture
    l : int
        the `l` degree of the integral
    r : int
        the `r` degree of the integral
    idata : 1-D array-like
        the array of interaction data
    model : str
        the interaction model to be used, possible values:
            * 'ESA' (model given in the paper *Transport Properties of High-Temperature Mars-Atmosphere Components*)
            * 'BM' (Born-Mayer potential)
            * 'LJ' (Lennard-Jones potential)
            * 'MLJ' (Modified Lennard-Jones model)
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'Switch' (returns the result for the Lennard-Jones model when :math:`T / \\varepsilon_{cd} < 10`
              and for the IPL potential otherwise)

        defaults to 'ESA'
    dimensional : bool
        if ``True``, then the dimensional :math:`\\Omega^{(l,r)}`-integral is returned, otherwise,
        the dimensionless :math:`\\Omega^{(l,r)}`-integral is returned (the dimensional integral divided by the
        integral of the same degrees calculated using the Rigid Sphere model), defaults to ``True``
    nokt : bool, optional
        if ``True`` and ``dimensional`` is ``True``,
        the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The :math:`\\Omega^{(l,r)}`-integral calculated using the selected potential

    Raises
    ------
    KineticlibError
        For the ``'VSS'``, ``'LJ'``, ``'IPL'`` and ``'Switch'`` models: if ``l!=r`` or ``l`` not in `{1,2}`,
        for the ``'ESA'`` model: if ``(l,r)`` not in `{(1,1),
        (1,2), (1,3), (1,4), (1,5), (2,2), (2,3), (2,4), (3,3), (4,4)}`
    """

    if model == 'ESA':
        if dimensional:
            return omega_dimensionless_esa(T, l, r, idata[13], idata[14]) * omega_rigid_sphere(T, l, r, idata[1],
                                                                                               idata[0], nokt)
        else:
            return omega_dimensionless_esa(T, l, r, idata[13], idata[14])
    elif model == 'Switch' and l == r:
        if T / idata[2] > 10:
            om_dimless = omega_dimensionless_BM(T, l, idata[1], idata[2], idata[3], idata[4])
        else:
            om_dimless = omega_dimensionless_LJ(T, l, idata[2])
        if dimensional:
            return om_dimless * omega_rigid_sphere(T, l, r, idata[1], idata[0], nokt)
        else:
            return om_dimless
    elif model == 'LJ' and l == r:
        if dimensional:
            return omega_dimensionless_LJ(T, l, idata[2]) * omega_rigid_sphere(T, l, l, idata[1], idata[0], nokt)
        else:
            return omega_dimensionless_LJ(T, l, idata[2])
    elif model == 'MLJ' and l == r:
        if dimensional:
            return omega_dimensionless_MLJ(T, l, idata[2]) * omega_rigid_sphere(T, l, l, idata[1], idata[0], nokt)
        else:
            return omega_dimensionless_MLJ(T, l, idata[2])
    elif model == 'IPL' and l == r:
        if dimensional:
            return omega_dimensionless_BM(T, l, idata[1], idata[2], idata[3], idata[4])\
                   * omega_rigid_sphere(T, l, r, idata[1], idata[0], nokt)
        else:
            return omega_dimensionless_BM(T, l, idata[1], idata[2], idata[3], idata[4])
    elif model == 'VSS' and l == r:
        if dimensional:
            return omega_vss(T, l, idata[0], idata[5 + 2 * (l - 1)], idata[6 + 2 * (l - 1)], nokt)
        else:
            return omega_vss(T, l, idata[0], idata[5 + 2 * (l - 1)], idata[6 + 2 * (l - 1)], nokt)\
                   / omega_rigid_sphere(T, l, r, idata[1], idata[0], False)
    elif model == 'RS':
        if dimensional:
            return omega_rigid_sphere(T, l, r, idata[1], idata[0], nokt)
        else:
            return 1.0
    else:
        raise KineticlibError('Cannot calculate the Omega^{(' + str(l) + ',' + str(r)
                              + ')} integral using the ' + model + ' potential')


def omega_rigid_sphere(T: float, l: int, r: int, sigma: float, mass: float, nokt: bool=False) -> float:
    """Returns the :math:`\\Omega^{(l,r)}`-integral for a rigid sphere potential for any ``l > 0`` and ``r > 0``

    Parameters
    ----------
    T : float
        the temperature of the mixture
    l : int
        the `l` degree of the integral
    r : int
        the `r` degree of the integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The calculated rigid sphere omega integral
    """
    if not nokt:
        mult = (T * constants.k / (2.0 * constants.pi * mass)) ** 0.5
    else:
        mult = (1.0 / (2.0 * constants.pi * mass)) ** 0.5

    return 0.5 * mult * constants.pi * factorial(r + 1) * (1.0 - 0.5 * (1.0 + (-1) ** l) / (l + 1)) * (sigma ** 2)


def omega_dimensionless_LJ(T: float, l: int, eps: float) -> float:
    """Returns the dimensionless :math:`\\Omega^{(l,l)}`-integral for the Lennard Jones potential (for
    ``l=1`` and ``l=2``)

    Parameters
    ----------
    T : float
        the temperature of the mixture
    l : int
        the `l` degree of the integral
    eps : float
        the Lennard-Jones :math:`\\varepsilon_{cd}` parameter, divided by Boltzmann's constant

    Returns
    -------
    float
        The dimensionless calculated Lennard-Jones omega integral

    Raises
    ------
    KineticlibError
        if ``l`` not in `{1,2}`
    """
    if l == 1:
        tmp = np.log(T / eps) + 1.4
        f = [-0.16845, -0.02258, 0.19779, 0.64373, -0.09267, 0.00711]
    elif l == 2:
        tmp = np.log(T / eps) + 1.5
        f = [-0.40811, -0.05086, 0.3401, 0.70375, -0.10699, 0.00763]
    else:
        raise KineticlibError('Cannot calculate the Omega^{(' + str(l) + ',' + str(l)
                              + ')} integral using the Lennard-Jones potentail')
    return 1.0 / (f[0] + f[1] / (tmp ** 2) + f[2] / tmp + f[3] * tmp
                + f[4] * (tmp ** 2) + f[5] * (tmp ** 3))


def omega_dimensionless_MLJ(T: float, l: int, eps: float) -> float:
    """Returns the dimensionless :math:`\\Omega^{(l,l)}`-integral using the modified Lennard-Jones model (for
    ``l=1`` and ``l=2``)

    Parameters
    ----------
    T : float
        the temperature of the mixture
    l : int
        the `l` degree of the integral
    eps : float
        the Lennard-Jones :math:`\\varepsilon_{cd}` parameter, divided by Boltzmann's constant

    Returns
    -------
    float
        The dimensionless calculated modified Lennard-Jones omega integral

    Raises
    ------
    KineticlibError
        if ``l`` not in `{1,2}`
    """
    return 0.9 * omega_dimensionless_LJ(T, l, eps) * ((T / 2000.) ** (-0.25))


def omega_dimensionless_BM(T: float, l: int, sigma: float, eps: float, phizero: float, beta: float) -> float:
    """Returns the dimensionless :math:`\\Omega^{(l,l)}`-integral for the Born-Mayer potential (for ``l=1`` and ``l=2``)

    Parameters
    ----------
    T : float
        the temperature of the mixture
    l : int
        the `l` degree of the integral
    sigma : float
        the collision diameter :math:`\\sigma_{cd}`
    eps : float
        the Lennard-Jones :math:`\\varepsilon_{cd}` parameter, divided by Boltzmann's constant
    phizero : float
        the IPL :math:`\\phi_{0}` parameter, divided by Boltzmann's constant
    beta : float
        the IPL :math:`\\beta` parameter

    Returns
    -------
    float
        The dimensionless calculated IPL omega integral

    Raises
    ------
    KineticlibError
        if ``l`` not in `{1,2}`
    """
    Tstar = T / eps
    vstar = phizero / eps
    rstar = 1.0 / (beta * sigma)
    Abig = np.zeros(3)
    if l == 1:
        a = np.array([[-267.0, 201.57, 174.672, 54.305],
                      [26700, -19226.5, -27693.8, -10860.9],
                      [-8.9, 6.3201, 10.227, 5.4304]])
        a[2, :] = a[2, :] * 100000
        coeff = 0.89
        pows = np.array([2, 4, 6])
        TT = Tstar
    elif l == 2:
        a = np.array([[-33.0838, 20.0862, 72.1059, 68.5001],
                      [101.571, -56.4472, -286.393, -315.4531],
                      [-87.7036, 46.313, 227.146, 363.1807]])
        coeff = 1.04
        pows = np.array([2, 3, 4])
        TT = np.log(Tstar)
    else:
        raise KineticlibError('Cannot calculate the Omega^{(' + str(l) + ',' + str(l)
                              + ')} integral using the IPL potential')
    Abig[:] = a[:, 0] + (a[:, 1] + a[:, 2] / np.log(vstar / 10)
                         + a[:, 3] / ((np.log(vstar / 10)) ** 2)) / ((rstar * np.log(vstar / 10)) ** 2)
    return (coeff + Abig[0] / (TT ** pows[0]) + Abig[1] / (TT ** pows[1]) + Abig[2] / (TT ** pows[2])) *\
           ((rstar * np.log(vstar / Tstar)) ** 2)


def omega_vss(T: float, l: int, mass: float, vssc: float, vsso: float, nokt: bool=False) -> float:
    """Returns the dimensionless :math:`\\Omega^{(l,l)}`-integral for the VSS potential (for ``l=1`` and ``l=2``)

    Parameters
    ----------
    T : float
        the temperature of the mixture
    l : int
        the `l` degree of the integral
    mass : float
        the collision-reduced mass :math:`m_{cd}`
    vssc : float
        the VSS potential :math:`C` parameter
    vsso : float
        the VSS potential :math:`\\omega` parameter
    nokt : bool, optional
        if ``True``, the result will be multiplied by :math:`\\sqrt{(1 / kT)}`, defaults to ``False``

    Returns
    -------
    float
        The dimensionless calculated VSS omega integral

    Raises
    ------
    KineticlibError
        if ``l`` not in `{1,2}`
    """
    if not nokt:
        mult = ((T * constants.k / (2 * constants.pi * mass)) ** 0.5)
    else:
        mult = ((1 / (2 * constants.pi * mass)) ** 0.5)
    if l == 1:
        return 0.5 * vssc * mult * gamma(3 - vsso) * (constants.physical_constants['Angstrom star'][0] ** 2)\
                   * (T ** (-vsso))
    elif l == 2:
        return 0.5 * vssc * mult * gamma(4 - vsso) * (constants.physical_constants['Angstrom star'][0] ** 2)\
                   * (T ** (-vsso))
    else:
        raise KineticlibError('Cannot calculate the Omega^{(' + str(l) + ',' + str(l)
                              + ')} integral using the VSS potential')


def omega_dimensionless_esa(T: float, l: int, r: int, beta: float, eps: float) -> float:
    """Returns the dimensionless :math:`\\Omega^{(l,r)}`-integral calculated using ESA data

    Parameters
    ----------
    T : float
        the temperature of the mixture
    l : int
        the `l` degree of the integral
    r : int
        the `r` degree of the integral
    beta : float
        the math:`\\beta` parameter for the ESA model
    eps : float
        the :math:`\\varepsilon_{0}` parameter for the ESA model

    Returns
    -------
    float
        The dimensionless calculated ESA omega integral

    Raises
    ------
    KineticlibError
        if ``(l,r)`` not in `{(1,1), (1,2), (1,3), (1,4), (1,5), (2,2), (2,3), (2,4), (3,3), (4,4)}`
    """
    x = np.log(T * constants.k / eps)
    coeff_array = np.zeros([7, 3])
    a = np.zeros(7)
    beta_pow_array = np.array([1.0, beta, beta ** 2])
    if l == 1 and r == 1:
        coeff_array[0, 0] = 7.884756 * (10 ** (-1))
        coeff_array[0, 1] = -2.438494 * (10 ** (-2))
        coeff_array[1, 0] = -2.952759 * (10 ** (-1))
        coeff_array[1, 1] = -1.744149 * (10 ** (-3))
        coeff_array[2, 0] = 5.020892 * (10 ** (-1))
        coeff_array[2, 1] = 4.316985 * (10 ** (-2))
        coeff_array[3, 0] = -9.042460 * (10 ** (-1))
        coeff_array[3, 1] = -4.017103 * (10 ** (-2))

        coeff_array[4, 0] = -3.373058
        coeff_array[4, 1] = 2.458538 * (10 ** (-1))
        coeff_array[4, 2] = -4.850047 * (10 ** (-3))
        coeff_array[5, 0] = 4.161981
        coeff_array[5, 1] = 2.202737 * (10 ** (-1))
        coeff_array[5, 2] = -1.718010 * (10 ** (-2))
        coeff_array[6, 0] = 2.462523
        coeff_array[6, 1] = 3.231308 * (10 ** (-1))
        coeff_array[6, 2] = -2.281072 * (10 ** (-2))
    elif l == 1 and r == 2:
        coeff_array[0, 0] = 7.123565 * (10 ** (-1))
        coeff_array[0, 1] = -2.688875 * (10 ** (-2))
        coeff_array[1, 0] = -2.910530 * (10 ** (-1))
        coeff_array[1, 1] = -2.065175 * (10 ** (-3))
        coeff_array[2, 0] = 4.187065 * (10 ** (-2))
        coeff_array[2, 1] = 4.060236 * (10 ** (-2))
        coeff_array[3, 0] = -9.287685 * (10 ** (-1))
        coeff_array[3, 1] = -2.342270 * (10 ** (-2))

        coeff_array[4, 0] = -3.598542
        coeff_array[4, 1] = 2.545120 * (10 ** (-1))
        coeff_array[4, 2] = -4.685966 * (10 ** (-3))
        coeff_array[5, 0] = 3.934824
        coeff_array[5, 1] = 2.699944 * (10 ** (-1))
        coeff_array[5, 2] = -2.009886 * (10 ** (-2))
        coeff_array[6, 0] = 2.578084
        coeff_array[6, 1] = 3.449024 * (10 ** (-1))
        coeff_array[6, 2] = -2.292710 * (10 ** (-2))
    elif l == 1 and r == 3:
        coeff_array[0, 0] = 6.606022 * (10 ** (-1))
        coeff_array[0, 1] = -2.831448 * (10 ** (-2))
        coeff_array[1, 0] = -2.870900 * (10 ** (-1))
        coeff_array[1, 1] = -2.232827 * (10 ** (-3))
        coeff_array[2, 0] = -2.519690 * (10 ** (-1))
        coeff_array[2, 1] = 3.778211 * (10 ** (-2))
        coeff_array[3, 0] = -9.173046 * (10 ** (-1))
        coeff_array[3, 1] = -1.864476 * (10 ** (-2))

        coeff_array[4, 0] = -3.776812
        coeff_array[4, 1] = 2.552528 * (10 ** (-1))
        coeff_array[4, 2] = -4.237220 * (10 ** (-3))
        coeff_array[5, 0] = 3.768103
        coeff_array[5, 1] = 3.155025 * (10 ** (-1))
        coeff_array[5, 2] = -2.218849 * (10 ** (-2))
        coeff_array[6, 0] = 2.695440
        coeff_array[6, 1] = 3.597998 * (10 ** (-1))
        coeff_array[6, 2] = -2.267102 * (10 ** (-2))
    elif l == 1 and r == 4:
        coeff_array[0, 0] = 6.268016 * (10 ** (-1))
        coeff_array[0, 1] = -2.945078 * (10 ** (-2))
        coeff_array[1, 0] = -2.830834 * (10 ** (-1))
        coeff_array[1, 1] = -2.361273 * (10 ** (-3))
        coeff_array[2, 0] = -4.559927 * (10 ** (-1))
        coeff_array[2, 1] = 3.705640 * (10 ** (-2))
        coeff_array[3, 0] = -9.334638 * (10 ** (-1))
        coeff_array[3, 1] = -1.797329 * (10 ** (-2))

        coeff_array[4, 0] = -3.947019
        coeff_array[4, 1] = 2.446843 * (10 ** (-1))
        coeff_array[4, 2] = -3.176374 * (10 ** (-3))
        coeff_array[5, 0] = 3.629926
        coeff_array[5, 1] = 3.761272 * (10 ** (-1))
        coeff_array[5, 2] = -2.451016 * (10 ** (-2))
        coeff_array[6, 0] = 2.824905
        coeff_array[6, 1] = 3.781709 * (10 ** (-1))
        coeff_array[6, 2] = -2.251978 * (10 ** (-2))
    elif l == 1 and r == 5:
        coeff_array[0, 0] = 5.956859 * (10 ** (-1))
        coeff_array[0, 1] = -2.915893 * (10 ** (-2))
        coeff_array[1, 0] = -2.804989 * (10 ** (-1))
        coeff_array[1, 1] = -2.298968 * (10 ** (-3))
        coeff_array[2, 0] = -5.965551 * (10 ** (-1))
        coeff_array[2, 1] = 3.724395 * (10 ** (-2))
        coeff_array[3, 0] = -8.946001 * (10 ** (-1))
        coeff_array[3, 1] = -2.550731 * (10 ** (-2))

        coeff_array[4, 0] = -4.076798
        coeff_array[4, 1] = 1.983892 * (10 ** (-1))
        coeff_array[4, 2] = -5.014065 * (10 ** (-4))
        coeff_array[5, 0] = 3.458362
        coeff_array[5, 1] = 4.770695 * (10 ** (-1))
        coeff_array[5, 2] = -2.678054 * (10 ** (-2))
        coeff_array[6, 0] = 2.982260
        coeff_array[6, 1] = 4.014572 * (10 ** (-1))
        coeff_array[6, 2] = -2.142580 * (10 ** (-2))
    elif l == 2 and r == 2:
        coeff_array[0, 0] = 7.898524 * (10 ** (-1))
        coeff_array[0, 1] = -2.114115 * (10 ** (-2))
        coeff_array[1, 0] = -2.998325 * (10 ** (-1))
        coeff_array[1, 1] = -1.243977 * (10 ** (-3))
        coeff_array[2, 0] = 7.077103 * (10 ** (-1))
        coeff_array[2, 1] = 3.583907 * (10 ** (-2))
        coeff_array[3, 0] = -8.946857 * (10 ** (-1))
        coeff_array[3, 1] = -2.473947 * (10 ** (-2))

        coeff_array[4, 0] = -2.958969
        coeff_array[4, 1] = 2.303358 * (10 ** (-1))
        coeff_array[4, 2] = -5.226562 * (10 ** (-3))
        coeff_array[5, 0] = 4.348412
        coeff_array[5, 1] = 1.920321 * (10 ** (-1))
        coeff_array[5, 2] = -1.496557 * (10 ** (-2))
        coeff_array[6, 0] = 2.205440
        coeff_array[6, 1] = 2.567027 * (10 ** (-1))
        coeff_array[6, 2] = -1.861359 * (10 ** (-2))
    elif l == 2 and r == 3:
        coeff_array[0, 0] = 7.269006 * (10 ** (-1))
        coeff_array[0, 1] = -2.233866 * (10 ** (-2))
        coeff_array[1, 0] = -2.972304 * (10 ** (-1))
        coeff_array[1, 1] = -1.392888 * (10 ** (-3))
        coeff_array[2, 0] = 3.904230 * (10 ** (-1))
        coeff_array[2, 1] = 3.231655 * (10 ** (-2))
        coeff_array[3, 0] = -9.442201 * (10 ** (-1))
        coeff_array[3, 1] = -1.494805 * (10 ** (-2))

        coeff_array[4, 0] = -3.137828
        coeff_array[4, 1] = 2.347767 * (10 ** (-1))
        coeff_array[4, 2] = -4.963979 * (10 ** (-3))
        coeff_array[5, 0] = 4.190370
        coeff_array[5, 1] = 2.346004 * (10 ** (-1))
        coeff_array[5, 2] = -1.718963 * (10 ** (-2))
        coeff_array[6, 0] = 2.319751
        coeff_array[6, 1] = 2.700236 * (10 ** (-1))
        coeff_array[6, 2] = -1.854217 * (10 ** (-2))
    elif l == 2 and r == 4:
        coeff_array[0, 0] = 6.829159 * (10 ** (-1))
        coeff_array[0, 1] = -2.332763 * (10 ** (-2))
        coeff_array[1, 0] = -2.943232 * (10 ** (-1))
        coeff_array[1, 1] = -1.514322 * (10 ** (-3))
        coeff_array[2, 0] = 1.414623 * (10 ** (-1))
        coeff_array[2, 1] = 3.075351 * (10 ** (-2))
        coeff_array[3, 0] = -9.720228 * (10 ** (-1))
        coeff_array[3, 1] = -1.038869 * (10 ** (-2))

        coeff_array[4, 0] = -3.284219
        coeff_array[4, 1] = 2.243767 * (10 ** (-1))
        coeff_array[4, 2] = -3.913041 * (10 ** (-3))
        coeff_array[5, 0] = 4.011692
        coeff_array[5, 1] = 3.005083 * (10 ** (-1))
        coeff_array[5, 2] = -2.012373 * (10 ** (-2))
        coeff_array[6, 0] = 2.401249
        coeff_array[6, 1] = 2.943600 * (10 ** (-1))
        coeff_array[6, 2] = -1.884503 * (10 ** (-2))
    elif l == 3 and r == 3:
        coeff_array[0, 0] = 7.468781 * (10 ** (-1))
        coeff_array[0, 1] = -2.518134 * (10 ** (-2))
        coeff_array[1, 0] = -2.947438 * (10 ** (-1))
        coeff_array[1, 1] = -1.811571 * (10 ** (-3))
        coeff_array[2, 0] = 2.234096 * (10 ** (-1))
        coeff_array[2, 1] = 3.681114 * (10 ** (-2))
        coeff_array[3, 0] = -9.974591 * (10 ** (-1))
        coeff_array[3, 1] = -2.670805 * (10 ** (-2))

        coeff_array[4, 0] = -3.381787
        coeff_array[4, 1] = 2.372932 * (10 ** (-1))
        coeff_array[4, 2] = -4.239629 * (10 ** (-3))
        coeff_array[5, 0] = 4.094540
        coeff_array[5, 1] = 2.756466 * (10 ** (-1))
        coeff_array[5, 2] = -2.009227 * (10 ** (-2))
        coeff_array[6, 0] = 2.476087
        coeff_array[6, 1] = 3.300898 * (10 ** (-1))
        coeff_array[6, 2] = -2.223317 * (10 ** (-2))
    elif l == 4 and r == 4:
        coeff_array[0, 0] = 7.365470 * (10 ** (-1))
        coeff_array[0, 1] = -2.242357 * (10 ** (-2))
        coeff_array[1, 0] = -2.968650 * (10 ** (-1))
        coeff_array[1, 1] = -1.396696 * (10 ** (-3))
        coeff_array[2, 0] = 3.747555 * (10 ** (-1))
        coeff_array[2, 1] = 2.847063 * (10 ** (-2))
        coeff_array[3, 0] = -9.944036 * (10 ** (-1))
        coeff_array[3, 1] = -1.378926 * (10 ** (-2))

        coeff_array[4, 0] = -3.136655
        coeff_array[4, 1] = 2.176409 * (10 ** (-1))
        coeff_array[4, 2] = -3.899247 * (10 ** (-3))
        coeff_array[5, 0] = 4.145871
        coeff_array[5, 1] = 2.855836 * (10 ** (-1))
        coeff_array[5, 2] = -1.939452 * (10 ** (-2))
        coeff_array[6, 0] = 2.315532
        coeff_array[6, 1] = 2.842981 * (10 ** (-1))
        coeff_array[6, 2] = -1.874462 * (10 ** (-2))
    else:
        raise KineticlibError('Cannot calculate the Omega^{(' + str(l) + ',' + str(r)
                              + ')} integral using the ESA data')
    for i in range(7):
        a[i] = np.dot(coeff_array[i, :], beta_pow_array)

    dimless_omega = (a[0] + a[1] * x) * exp((x - a[2]) / a[3]) \
                                      / (exp((x - a[2]) / a[3]) + exp((a[2] - x) / a[3]))\
                    + a[4] * exp((x - a[5]) / a[6]) \
                           / (exp((x - a[5]) / a[6]) + exp((a[5] - x) / a[6]))
    return exp(dimless_omega)