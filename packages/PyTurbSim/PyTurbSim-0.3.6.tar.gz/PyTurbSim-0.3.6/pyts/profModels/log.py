"""
This module contains the log-law mean-velocity profiles:
 nwtc   - The NWTC logarithmic mean wind speed profile.
 H2O    - The hydro-logarithmic mean velocity profile.

"""
from .mBase import profModelBase, np, profObj
from ..misc import kappa, psiM


class nwtc(profModelBase,):

    r"""
    The NWTC logarithmic mean wind-speed profile.

    Parameters
    ----------
    URef :          float
        Reference velocity for the wind profile [m/s].
    ZRef :          float
        Reference height of the reference velocity [m].
    Z0 :            float
        Surface roughness length [m].
    Ri :            float
        The Richardon number [non-dimensional].
    turbmodel :     str, optional
        The name of the turbulence model in this simulationm.

    Notes
    -----

    The exact form of this model is,

    .. math::
       \bar{U}(z) = U_{Ref}\frac{ln( z / Z0 ) - \psi_M}{ln( Z_{Ref} / Z0) - \psi_M}

    Where psi_M is a function of Ri, the Richardson number (psi_M=0
    for Ri=0), and the turbulence model.

    """

    def __init__(self, URef, ZRef, Z0, Ri=0, turbmodel=None):
        self.Uref = URef
        self.Zref = ZRef
        self.Z0 = Z0
        self.Ri = Ri
        self.TurbModel = turbmodel

    def __call__(self, tsrun):
        """
        Create and calculate the mean-profile object for a `tsrun`
        instance.

        Parameters
        ----------
        tsrun :         :class:`tsrun <pyts.main.tsrun>`
                        A TurbSim run object.

        Returns
        -------
        out :           :class:`profObj <.mBase.profObj>`
                        A logarithmic wind-speed profile for the grid in `tsrun`.

        """
        out = profObj(tsrun)
        out[0] = self.model(out.grid.z)[:, None]
        return out

    def model(self, z):
        """
        Calculate the log profile for heights `z`.

        Parameters
        ----------
        z :     array_like(dtype=float)
                Height above the ground [m].

        Returns
        -------
        u :     array_like(dtype=float)
                The mean velocity array [m/s].

        """
        # Note: this function is separated from the __call__ routine so that it
        # can be utilized by other modules
        return (self.Uref * (np.log(z / self.Z0) + self.psiM) / (np.log(self.Zref / self.Z0) + self.psiM))

    @property
    def psiM(self,):
        """
        The psi_M parameter for this profile model.

        See the :func:`pyts.misc.psiM` function for details.
        """
        return psiM(self.Ri, self.TurbModel)


class H2O(profModelBase,):

    """
    The logarithmic mean water velocity profile.

    Parameters
    ----------
    URef :      float
                Reference velocity for the wind profile [m/s].
    ZRef :      float
                Reference height of the reference velocity [m].
    ustar :     float
                Surface friction veclocity [m/s].

    Notes
    -----

    The precise form of this model is,

    .. math::

           Ubar(z) = U_*/\kappa * \mathrm{Ln}( z / Z_{ref}) + U_{ref}

    """

    def __init__(self, Uref, Zref, ustar):
        self.Uref = Uref
        self.Zref = Zref
        self.Ustar = ustar

    def __call__(self, tsrun):
        """
        Create and calculate the mean-profile object for a `tsrun`
        instance.

        Parameters
        ----------
        tsrun : :class:`tsrun <pyts.main.tsrun>`
                A TurbSim run object.

        Returns
        -------
        out :   :class:`profObj <.mBase.profObj>`
                A logarithmic mean-velocity profile object for the
                spatial grid in tsrun.
        """
        out = profObj(tsrun)
        out[0] = (self.Ustar / kappa * np.log(
            out.grid.z / self.Zref) + self.Uref)[:, None]
        return out
