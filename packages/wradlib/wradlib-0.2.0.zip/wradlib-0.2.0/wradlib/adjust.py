#-------------------------------------------------------------------------------
# Name:         adjust
# Purpose:
#
# Authors:      Maik Heistermann, Stephan Jacobi and Thomas Pfaff
#
# Created:      26.10.2011
# Copyright:    (c) Maik Heistermann, Stephan Jacobi and Thomas Pfaff 2011
# Licence:      The MIT License
#-------------------------------------------------------------------------------
#!/usr/bin/env python

"""
Gage adjustment
^^^^^^^^^^^^^^^

Concept
-------

The objective of this module is the adjustment of radar-based rainfall estimates
by rain gage observations. However, this module could also be applied to adjust
satellite rainfall by rain gage observations, remotely sensed soil moisture
patterns by ground truthing moisture sensors, or any dense spatial point pattern
which could be adjusted by sparse point measurements (ground truth).

Basically, we only need two data sources:

- point observations (e.g. rain gage observations)

- set of (potentially irregular) unadjusted point values (e.g. remotely sensed rainfall)

[GoudenhooftdandDelobbe2009]_ provide an excellent overview of adjustment procedures.
The general idea is that we quantify the error of the remotely sensed rainfall
at the rain gage locations, assuming the rain gage observation to be accurate.
The error can be assumed to be purely additive (AdjustAdd), purely multiplicative
(AdjustMultiply, AdjustMFB) or a mixture of both (AdjustMixed). If the error is
assumed to heterogeneous in space (AdjustAdd, AdjustMultiply, AdjustMixed), the
error at the rain gage locations is interpolated to the radar bin locations and
then used to adjust (correct) the raw radar rainfall estimates. In case of the
AdjustMFB approach, though, the multiplicative error is assumed to be homogenoues
in space.

Quick start
-----------

The basic procedure consists of creating an adjustment object from the class you
want to use for adjustment. After that, you can call the object with the actual
data that is to be adjusted. The following example is using the additive error
model with default settings. ``obs_coords`` and ``raw_coords`` represent arrays with
coordinate pairs for the gage observations and the radar bins, respectively.
``obs`` and ``raw`` are arrays containing the actual data::

    adjuster = AdjustAdd(obs_coords, raw_coords)
    adjusted = adjuster(obs, raw)

The user can specify the approach that should be used to interpolate the error
in space, as well as the keyword arguments which control the behaviour of the
interpolation approach. For this purpose, all interpolation classes from the
wradlib.ipol module are available and can be passed by using the ``Ipclass``
argument. The default interpolation class is Inverse Distance Weighting
(wradlib.ipol.Idw). If you want to use e.g. linear barycentric interpolation::

    import wradlib.ipol as ipol
    adjuster = AdjustAdd(obs_coords, raw_coords, Ipclass=ipol.Linear)
    adjusted = adjuster(obs, raw)

Cross validation
----------------

Another helpful feature is an easy-to-use method for `leave-one-out cross-validation
<http://en.wikipedia.org/wiki/Cross-validation_%28statistics%29>`_. Cross validation
is a standard procedure for verifying rain gage adjustment or interpolation procedures.
You can start the cross validation in the same way as you start the actual adjustment,
however, you call the ``xvalidate`` method instead. The result of the cross validation
are pairs of observation and the corresponding adjustment result at the observation
location. Using the wradlib.verify module, you can compute error metrics for the
cross validation results::

    adjuster = AdjustAdd(obs_coords, raw_coords)
    observed, estimated = adjuster.xvalidate(obs, raw)
    from wradlib.verify import ErrorMetrics
    metrics = ErrorMetrics(observed, estimated)
    metrics.report()

.. autosummary::
   :nosignatures:
   :toctree: generated/

   AdjustBase
   AdjustMFB
   AdjustMultiply
   AdjustAdd
   AdjustMixed
   Raw_at_obs
   GageOnly


References
----------

.. [GoudenhooftdandDelobbe2009] Goudenhoofdt, E., and L. Delobbe, 2009.
    Evaluation of radar-gauge merging methods for quantitative
    precipitation estimates. HESS, 13, 195-203. URL: http://www.hydrol-earth-syst-sci.net/13/195/2009/hess-13-195-2009.pdf


"""

# site packages
import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import linregress

# wradlib modules
import wradlib.ipol as ipol
import wradlib.util as util


class AdjustBase(ipol.IpolBase):
    """
    The basic adjustment class that inherits to all other classes

    All methods except the ``__call__`` method are inherited to the following adjustment classes.

    Parameters
    ----------
    obs_coords : array of float
        coordinate pairs of observations points
    raw_coords : array of float
        coordinate pairs of raw (unadjusted) field
    nnear_raws : integer
        defaults to 9
    stat : string
        defaults to 'median'
    mingages : integer
        minimum number of gages which are required for an adjustment
    minval : float
        If the gage or radar observation is below this threshold, the location
        will not be used for adjustment. For additive adjustment, this value
        should be set to zero (default value).
    Ipclass : an interpolation class from wradib.ipol
        Default value is wradlib.ipol.Idw (Inverse Distance Weighting)
    ipargs : keyword arguments to create an instance of Ipclass
        For wradlib.ipol.Idw, these keywird arguments woudl e.g. be nnear or p

    Examples
    --------
    >>> import wradlib.adjust as adjust
    >>> import numpy as np
    >>> import pylab as pl
    >>> pl.interactive(True)
    >>> # 1-d example including all available adjustment methods
    >>> # --------------------------------------------------------------------------
    >>> # gage and radar coordinates
    >>> obs_coords = np.array([5,10,15,20,30,45,65,70,77,90])
    >>> radar_coords = np.arange(0,101)
    >>> # true rainfall
    >>> truth = np.abs(np.sin(0.1*radar_coords))
    >>> # radar error
    >>> erroradd = np.random.uniform(0,0.5,len(radar_coords))
    >>> errormult= 1.1
    >>> # radar observation
    >>> radar = errormult*truth + erroradd
    >>> # gage observations are assumed to be perfect
    >>> obs = truth[obs_coords]
    >>> # add a missing value to observations (just for testing)
    >>> obs[1] = np.nan
    >>> # adjust the radar observation by additive model
    >>> add_adjuster = adjust.AdjustAdd(obs_coords, radar_coords, nnear_raws=1)
    >>> add_adjusted = add_adjuster(obs, radar)
    >>> # adjust the radar observation by multiplicative model
    >>> mult_adjuster = adjust.AdjustMultiply(obs_coords, radar_coords, nnear_raws=1)
    >>> # TODO: had to strip argument 3
    >>> # mult_adjusted = mult_adjuster(obs, radar, 0.)
    >>> mult_adjusted = mult_adjuster(obs, radar)
    >>> # adjust the radar observation by MFB
    >>> mfb_adjuster = adjust.AdjustMFB(obs_coords, radar_coords, nnear_raws=1)
    >>> mfb_adjusted = mfb_adjuster(obs, radar, 0.)
    >>> # adjust the radar observation by AdjustMixed
    >>> mixed_adjuster = adjust.AdjustMixed(obs_coords, radar_coords, nnear_raws=1)
    >>> mixed_adjusted = mixed_adjuster(obs, radar)
    >>> line1 = pl.plot(radar_coords, radar, 'k-', label="raw radar")
    >>> line2 = pl.plot(obs_coords, obs, 'ro', label="gage obs")
    >>> line3 = pl.plot(radar_coords, add_adjusted, '-', color="red", label="adjusted by AdjustAdd")
    >>> line4 = pl.plot(radar_coords, mult_adjusted, '-', color="green", label="adjusted by AdjustMultiply")
    >>> line5 = pl.plot(radar_coords, mfb_adjusted, '-', color="orange", label="adjusted by AdjustMFB")
    >>> line6 = pl.plot(radar_coords, mixed_adjusted, '-', color="blue", label="adjusted by AdjustMixed")
    >>> lgnd = pl.legend()
    >>> pl.show()

    """
    def __init__(self, obs_coords, raw_coords, nnear_raws=9, stat='median', mingages=5, minval=0., Ipclass=ipol.Idw, **ipargs):
        # These are the coordinates of the rain gage locations and the radar bin locations
        self.obs_coords     = self._make_coord_arrays(obs_coords)
        self.raw_coords     = self._make_coord_arrays(raw_coords)
        # These are the general control parameters for all adjustment procedures
        self.nnear_raws     = nnear_raws
        self.stat           = stat
        self.mingages       = mingages
        self.minval         = minval
        # This method will quickly retrieve the actual radar values at the gage locations
        self.get_raw_at_obs = Raw_at_obs(self.obs_coords,  self.raw_coords, nnear=nnear_raws, stat=stat)
        # remember the interpolation class and its keyword arguments as attributes
        self.Ipclass        = Ipclass
        self.ipargs         = ipargs
        # create a default instance of interpolator
        self.ip             = Ipclass(src=self.obs_coords, trg=self.raw_coords, **ipargs)
    def _checkip(self, ix, targets):
        """INTERNAL: Return a revised instance of the Interpolator class.

        When an instance of an Adjust... class is created, an instance of the desired
        Interpolation class (argument Ipclass) is created as attribute *self.ip*). However,
        this instance is only valid in case all observation points (attribute *self.obs_coords*)
        have valid obsservation-radar pairs. In case points are missing (or in case the
        instance is called in the sourse of cross validation), a new instance has to
        be created which consideres the new constellation of observation-radar pairs.
        This method computes and returns this new instance.

        Parameters
        ----------
        ix : array of integers
            These are the indices of observation points with valid observation-radar pairs
        targets : array of floats of shape (number of target points, 2)
            Target coordinates for the interpolation

        Returns
        -------
        output : an instance of a class that inherited from wradlib.ipol.IpolBase

        """
        #    first, set interpolation targets (default: the radar coordinates)
        targets_default = False
        if targets==None:
            targets = self.raw_coords
            targets_default = True
        #    second, compute inverse distance neighbours
        if (not len(ix)==len(self.obs_coords)) or (not targets_default):
            return self.Ipclass(self.obs_coords[ix], targets, **self.ipargs)
        else:
            return self.ip
    def __call__(self, obs, raw, targets=None):
        """Empty prototype
        """
        pass
    def _check_shape(self, obs, raw):
        """INTERNAL: Check consistency of the input data obs and raw with the shapes of the coordinates
        """
        # TODO
        pass
    def _get_valid_pairs(self, obs, raw):
        """INTERNAL: Helper method to identify valid obs-raw pairs
        """
        # checking input shape consistency
        self._check_shape(obs, raw)
        # radar values at gage locations
        rawatobs = self.get_raw_at_obs(raw, obs)
        # check where both gage and radar observations are valid
        ix = np.intersect1d( util._idvalid(obs, minval=self.minval),  util._idvalid(rawatobs, minval=self.minval))
        return rawatobs, ix
    def xvalidate(self, obs, raw):
        """Leave-One-Out Cross Validation, applicable to all gage adjustment classes.

        This method will be inherited to other Adjust classes. It should thus be
        applicable to all adjustment procedures without any modification. This way,
        the actual adjustment procedure has only to be defined *once* in the __call__ method.

        The output of this method can be evaluated by using the `verify.ErrorMetrics` class.

        Parameters
        ----------
        obs : array of floats
        raw : array of floats

        Returns
        -------
        obs : array of floats
            valid observations at those locations which have a valid radar observation
        estatobs : array of floats
            estimated values at the valid observation locations

        """
        rawatobs, ix = self._get_valid_pairs(obs, raw)
        self.get_raws_directly_at_obs = Raw_at_obs(self.obs_coords,  self.raw_coords, nnear=1)
        raws_directly_at_obs = self.get_raws_directly_at_obs(raw)
        ix = np.intersect1d( ix,  util._idvalid(raws_directly_at_obs, minval=self.minval))
        # Container for estimation results at the observation location
        estatobs = np.zeros(obs.shape)*np.nan
        # check whether enough gages remain for adjustment
        if len(ix)<=(self.mingages-1):
            # not enough gages for cross validation: return empty arrays
            return obs, estatobs
        # Now iterate over valid pairs
        for i in ix:
            # Pass all valid pairs except ONE which you pass as target
            ix_adjust = np.setdiff1d(ix, [i])
            estatobs[i] = self.__call__(obs, raws_directly_at_obs[i], self.obs_coords[i].reshape((1,-1)), rawatobs, ix_adjust)
        return obs, estatobs


class AdjustAdd(AdjustBase):
    """Gage adjustment using an additive error model.

    First, an instance of AdjustAdd has to be created. Calling this instance then
    does the actual adjustment. The motivation behind this performance. In case
    the observation points are always the same for different time steps, the computation
    of neighbours and invserse distance weights only needs to be performed once.

    AdjustAdd automatically takes care of invalid gage or radar observations (e.g.
    NaN, Inf or other typical missing data flags such as -9999. However, in case
    e.g. the observation data contain missing values, the computation of the inverse
    distance weights needs to be repeated in __call__ which is at the expense of
    performance.

    Parameters
    ----------
    obs_coords : array of float
        coordinate pairs of observations points
    raw_coords : array of float
        coordinate pairs of raw (unadjusted) field
    nnear_raws : integer
        defaults to 9
    stat : string
        defaults to 'median'
    mingages : integer
        minimum number of gages which are required for an adjustment
    minval : float
        If the gage or radar observation is below this threshold, the location
        will not be used for adjustment. For additive adjustment, this value
        should be set to zero (default value).
    Ipclass : an interpolation class from wradib.ipol
        Default value is wradlib.ipol.Idw (Inverse Distance Weighting)
    ipargs : keyword arguments to create an instance of Ipclass
        For wradlib.ipol.Idw, these keywird arguments woudl e.g. be nnear or p

    Returns
    -------
    output : array of adjusted radar values

    Notes
    -----
    Inherits from AdjustBase

    """

    def __call__(self, obs, raw, targets=None, rawatobs=None, ix=None):
        """
        Return the field of *raw* values adjusted by *obs*.

        Parameters
        ----------
        obs : array of floats
            Gage observations
        raw : array of floats
            Raw unadjusted radar rainfall
        targets : (INTERNAL) array of floats
            Coordinate pairs for locations on which the final adjustment product is interpolated
            Defaults to None. In this case, the output locations will be identical to the radar coordinates
        rawatobs : (INTERNAL) array of floats
            For internal use from AdjustBase.xvalidate only (defaults to None)
        ix : (INTERNAL) array of integers
            For internal use from AdjustBase.xvalidate only (defaults to None)

        """
        # ----------------GENERIC PART FOR MOST __call__ methods----------------
        if None in [ix, rawatobs]:
            # Check for valid observation-radar pairs in case this method has not been called from self.xvalidate
            rawatobs, ix = self._get_valid_pairs(obs, raw)
        if len(ix)<=self.mingages:
            # Not enough valid gages for adjustment? - return unadjusted data
            return raw
        # Get new Interpolator instance if necessary
        ip = self._checkip(ix, targets)

        # -----------------THIS IS THE ACTUAL ADJUSTMENT APPROACH---------------
        # The error is a difference
        error = obs[ix] - rawatobs[ix]
        # interpolate the error field
        iperror = ip(error)
        # add error field to raw and make sure no negatives occur
        return np.where( (raw + iperror)<0., 0., raw + iperror)



class AdjustMultiply(AdjustBase):
    """Gage adjustment using a multiplicative error model

    First, an instance of AdjustMultiply has to be created. Calling this instance then
    does the actual adjustment. The motivation behind this performance. In case
    the observation points are always the same for different time steps, the computation
    of neighbours and invserse distance weights only needs to be performed once during
    initialisation.

    AdjustMultiply automatically takes care of invalid gage or radar observations (e.g.
    NaN, Inf or other typical missing data flags such as -9999. However, in case
    e.g. the observation data contain missing values, the computation of the inverse
    distance weights needs to be repeated in __call__ which is at the expense of
    performance.

    Parameters
    ----------
    obs_coords : array of float
        coordinate pairs of observations points
    raw_coords : array of float
        coordinate pairs of raw (unadjusted) field
    nnear_raws : integer
        defaults to 9
    stat : string
        defaults to 'median'
    mingages : integer
        minimum number of gages which are required for an adjustment
    minval : float
        If the gage or radar observation is below this threshold, the location
        will not be used for adjustment. For additive adjustment, this value
        should be set to zero (default value).
    Ipclass : an interpolation class from wradib.ipol
        Default value is wradlib.ipol.Idw (Inverse Distance Weighting)
    ipargs : keyword arguments to create an instance of Ipclass
        For wradlib.ipol.Idw, these keywird arguments woudl e.g. be nnear or p

    Returns
    -------
    output : array of adjusted radar values

    Notes
    -----
    Inherits from AdjustBase

    """

    def __call__(self, obs, raw, targets=None, rawatobs=None, ix=None):
        """
        Return the field of *raw* values adjusted by *obs*.

        Parameters
        ----------
        obs : array of floats
            Gage observations
        raw : array of floats
            Raw unadjusted radar rainfall
        targets : (INTERNAL) array of floats
            Coordinate pairs for locations on which the final adjustment product is interpolated
            Defaults to None. In this case, the output locations will be identical to the radar coordinates
        rawatobs : (INTERNAL) array of floats
            For internal use from AdjustBase.xvalidate only (defaults to None)
        ix : (INTERNAL) array of integers
            For internal use from AdjustBase.xvalidate only (defaults to None)

        """
        # ----------------GENERIC PART FOR MOST __call__ methods----------------
        if None in [ix, rawatobs]:
            # Check for valid observation-radar pairs in case this method has not been called from self.xvalidate
            rawatobs, ix = self._get_valid_pairs(obs, raw)
        if len(ix)<=self.mingages:
            # Not enough valid gages for adjustment? - return unadjusted data
            return raw
        # Get new Interpolator instance if necessary
        ip = self._checkip(ix, targets)

        # -----------------THIS IS THE ACTUAL ADJUSTMENT APPROACH---------------
        # computing the error
        error = obs[ix] / rawatobs[ix]
        # interpolate error field
        iperror = ip(error)
        # multiply error field with raw
        return iperror * raw


class AdjustMixed(AdjustBase):
    """Gage adjustment using a mixed error model (additive and multiplicative).

    The mixed error model assumes that you have both a multiplicative and an
    additive error term. The intention is to overcome the drawbacks of the purely
    additive and multiplicative approaches (see AdjustAdd and AdjustMultiply). The
    formal reprentation of the error model according to [Pfaff2010]_ is:

    R(gage) = R(radar) * (1+delta) + epsilon

    delta and epsilon have to be assumed to be independent and normally distributed.
    The present implementation is based on a Least Squares estimation of delta and
    epsilon for each rain gage location. delta and epsilon are then interpolated
    and used to correct the radar rainfall field. The least squares implementation
    uses the equation for the error model plus the condition to minimize
    (delta**2 + epsilon**2) for each gage location. The idea behind this is that epsilon
    dominates the adjustment for small deviations between radar and gage while
    delta dominates in case of large deviations.

    **Usage**: First, an instance of AdjustMMixed has to be created. Calling this instance then
    does the actual adjustment. The motivation behind this is performance. In case
    the observation points are always the same for different time steps, the computation
    of neighbours and invserse distance weights only needs to be performed once during
    initialisation.

    AdjustMixed automatically takes care of invalid gage or radar observations (e.g.
    NaN, Inf or other typical missing data flags such as -9999. However, in case
    e.g. the observation data contain missing values, the computation of the inverse
    distance weights needs to be repeated in __call__ which is at the expense of
    performance.

    Parameters
    ----------
    obs_coords : array of float
        coordinate pairs of observations points
    raw_coords : array of float
        coordinate pairs of raw (unadjusted) field
    nnear_raws : integer
        defaults to 9
    stat : string
        defaults to 'median'
    mingages : integer
        minimum number of gages which are required for an adjustment
    minval : float
        If the gage or radar observation is below this threshold, the location
        will not be used for adjustment. For additive adjustment, this value
        should be set to zero (default value).
    Ipclass : an interpolation class from wradib.ipol
        Default value is wradlib.ipol.Idw (Inverse Distance Weighting)
    ipargs : keyword arguments to create an instance of Ipclass
        For wradlib.ipol.Idw, these keywird arguments woudl e.g. be nnear or p

    Returns
    -------
    output : array of adjusted radar values

    Notes
    -----
    Inherits from AdjustBase

    References
    ----------
    .. [Pfaff2010] Pfaff, T., 2010. Radargestuetzte Schaetzung von Niederschlagsensembles (in German).
        In: Bronstert et al. (Eds.). Operationelle Abfluss- und Hochwasservorhersage in Quellgebieten.
        Final Project Report, pp. 113-118. URL: http://www.rimax-hochwasser.de/fileadmin/user_uploads/RIMAX_PUB_22_0015_Abschlussbericht%20OPAQUE_final.pdf.

    """

    def __call__(self, obs, raw, targets=None, rawatobs=None, ix=None):
        """
        Return the field of *raw* values adjusted by *obs*.

        Parameters
        ----------
        obs : array of floats
            Gage observations
        raw : array of floats
            Raw unadjusted radar rainfall
        targets : (INTERNAL) array of floats
            Coordinate pairs for locations on which the final adjustment product is interpolated
            Defaults to None. In this case, the output locations will be identical to the radar coordinates
        rawatobs : (INTERNAL) array of floats
            For internal use from AdjustBase.xvalidate only (defaults to None)
        ix : (INTERNAL) array of integers
            For internal use from AdjustBase.xvalidate only (defaults to None)

        """
        # ----------------GENERIC PART FOR MOST __call__ methods----------------
        if None in [ix, rawatobs]:
            # Check for valid observation-radar pairs in case this method has not been called from self.xvalidate
            rawatobs, ix = self._get_valid_pairs(obs, raw)
        if len(ix)<=self.mingages:
            # Not enough valid gages for adjustment? - return unadjusted data
            return raw
        # Get new Interpolator instance if necessary
        ip = self._checkip(ix, targets)

        # -----------------THIS IS THE ACTUAL ADJUSTMENT APPROACH---------------
        # computing epsilon and delta from least squares
        epsilon = (obs[ix] - rawatobs[ix]) / (rawatobs[ix]**2 + 1.)
        delta   = ( (obs[ix] - epsilon) / rawatobs[ix] ) - 1.
        # interpolate error fields
        ipepsilon = ip(epsilon)
        ipdelta = ip(delta)
        # compute adjusted radar rainfall field
        return (1. + ipdelta) * raw + ipepsilon



class AdjustMFB(AdjustBase):
    """
    Multiplicative gage adjustment using *one* correction factor for the entire domain

    This method is also known as the Mean Field Bias correction

    Parameters
    ----------
    obs_coords : array of float
        coordinate pairs of observations points
    raw_coords : array of float
        coordinate pairs of raw (unadjusted) field
    nnear_raws : integer
        defaults to 9
    stat : string
        defaults to 'median'
    mingages : integer
        minimum number of gages which are required for an adjustment
    minval : float
        If the gage or radar observation is below this threshold, the location
        will not be used for adjustment. For additive adjustment, this value
        should be set to zero (default value).
    Ipclass : an interpolation class from wradib.ipol
        Default value is wradlib.ipol.Idw (Inverse Distance Weighting)
    ipargs : keyword arguments to create an instance of Ipclass
        For wradlib.ipol.Idw, these keywird arguments woudl e.g. be nnear or p

    Returns
    -------
    output : array of adjusted radar values

    Notes
    -----
    Inherits from AdjustBase

    """

    def __call__(self, obs, raw, targets=None, rawatobs=None, ix=None, biasby="linregr"):
        """
        Return the field of *raw* values adjusted by *obs*.

        Parameters
        ----------
        obs : array of floats
            Gage observations
        raw : array of floats
            Raw unadjusted radar rainfall
        biasby : string
            The method which is used to compute the mean field bias. Defaults to
            "linregr" which fits a regression line through observed and estimated values
            and than gets the bias from the inverse of the slope.
        targets : (INTERNAL) array of floats
            Coordinate pairs for locations on which the final adjustment product is interpolated
            Defaults to None. In this case, the output locations will be identical to the radar coordinates
        rawatobs : (INTERNAL) array of floats
            For internal use from AdjustBase.xvalidate only (defaults to None)
        ix : (INTERNAL) array of integers
            For internal use from AdjustBase.xvalidate only (defaults to None)

        """
        # ----------------GENERIC PART FOR MOST __call__ methods----------------
        if None in [ix, rawatobs]:
            # Check for valid observation-radar pairs in case this method has not been called from self.xvalidate
            rawatobs, ix = self._get_valid_pairs(obs, raw)
        if len(ix)<=self.mingages:
            # Not enough valid gages for adjustment? - return unadjusted data
            return raw
##        # Get new Interpolator instance if necessary
##        ip = self._checkip(ix, targets)

        # -----------------THIS IS THE ACTUAL ADJUSTMENT APPROACH---------------
        # compute ratios for each valid observation point
        ratios = np.ma.masked_invalid(obs[ix] / rawatobs[ix])
        if len(np.where(np.logical_not(ratios.mask))[0]) < self.mingages:
            # Not enough valid pairs of raw and obs
            return raw
        if biasby=="mean":
            corrfact = np.mean(ratios)
        elif biasby=="median":
            corrfact = np.median(ratios)
        elif biasby=="linregr":
            ix_ = np.where(np.logical_not(ratios.mask))[0]
            x = obs[ix][ix_]
            y = rawatobs[ix][ix_]
            # check whether we should adjust or not
            try:
                slope,intercept,r,p,stderr=linregress(x,y)
            except:
                slope, r, p = 0, 0, np.inf
            if slope > 0.1 and r > 0.5 and p < 0.01:
                x = x[:,np.newaxis]
                try:
                    slope, _,_,_ = np.linalg.lstsq(x,y)
                    if not slope[0]==0:
                        corrfact = 1. / slope[0]
                    else:
                        corrfact = 1.
                except:
                    # no correction if linear regression fails
                    corrfact = 1.
            else:
                corrfact=1.
        else:
            print("WARNING: Invalid <biasby> argument value for AdjustMFB: %s" % biasby)
            print("         Using default value biasby='mean' instead.")
        if type(corrfact)==np.ma.core.MaskedConstant:
            corrfact = 1.
        # TODO: commented out, remove if not necessary
        # print "corrfact=",corrfact
        return corrfact*raw


class AdjustNone(AdjustBase):
    """
    Same behaviour as the other adjustment classes, but simply returns the unadjusted data

    Parameters
    ----------
    obs_coords : array of float
        coordinate pairs of observations points
    raw_coords : array of float
        coordinate pairs of raw (unadjusted) field
    nnear_raws : integer
        defaults to 9
    stat : string
        defaults to 'median'
    mingages : integer
        minimum number of gages which are required for an adjustment
    minval : float
        If the gage or radar observation is below this threshold, the location
        will not be used for adjustment. For additive adjustment, this value
        should be set to zero (default value).
    Ipclass : an interpolation class from wradib.ipol
        Default value is wradlib.ipol.Idw (Inverse Distance Weighting)
    ipargs : keyword arguments to create an instance of Ipclass
        For wradlib.ipol.Idw, these keywird arguments woudl e.g. be nnear or p

    Returns
    -------
    output : array of unadjusted radar values

    Notes
    -----
    Inherits from AdjustBase

    """

    def __call__(self, obs, raw, targets=None, rawatobs=None, ix=None):
        """
        Return the field of *raw* values adjusted by *obs* (here: no adjustment!)

        Parameters
        ----------
        obs : array of floats
            Gage observations
        raw : array of floats
            Raw unadjusted radar rainfall
        targets : (INTERNAL) array of floats
            Coordinate pairs for locations on which the final adjustment product is interpolated
            Defaults to None. In this case, the output locations will be identical to the radar coordinates
        rawatobs : (INTERNAL) array of floats
            For internal use from AdjustBase.xvalidate only (defaults to None)
        ix : (INTERNAL) array of integers
            For internal use from AdjustBase.xvalidate only (defaults to None)

        """
        # ----------------GENERIC PART FOR MOST __call__ methods----------------
        if None in [ix, rawatobs]:
            # Check for valid observation-radar pairs in case this method has not been called from self.xvalidate
            rawatobs, ix = self._get_valid_pairs(obs, raw)
        if len(ix)<=self.mingages:
            # Not enough valid gages for adjustment? - return unadjusted data
            return raw
        return raw


class GageOnly(AdjustBase):
    """Same behaviour as the other adjustment classes, but returns an interpolation of rain gage observations

    First, an instance of GageOnly has to be created. Calling this instance then
    does the actual adjustment. The motivation behind this performance. In case
    the observation points are always the same for different time steps, the computation
    of neighbours and invserse distance weights only needs to be performed once during
    initialisation.

    GageOnly automatically takes care of invalid gage or radar observations (e.g.
    NaN, Inf or other typical missing data flags such as -9999. However, in case
    e.g. the observation data contain missing values, the computation of the inverse
    distance weights needs to be repeated in __call__ which is at the expense of
    performance.

    Parameters
    ----------
    obs_coords : array of float
        coordinate pairs of observations points
    raw_coords : array of float
        coordinate pairs of raw (unadjusted) field
    nnear_raws : integer
        defaults to 9
    stat : string
        defaults to 'median'
    mingages : integer
        minimum number of gages which are required for an adjustment
    minval : float
        If the gage or radar observation is below this threshold, the location
        will not be used for adjustment. For additive adjustment, this value
        should be set to zero (default value).
    Ipclass : an interpolation class from wradib.ipol
        Default value is wradlib.ipol.Idw (Inverse Distance Weighting)
    ipargs : keyword arguments to create an instance of Ipclass
        For wradlib.ipol.Idw, these keywird arguments woudl e.g. be nnear or p

    Returns
    -------
    output : array of adjusted radar values

    Notes
    -----
    Inherits from AdjustBase

    """

    def __call__(self, obs, raw, targets=None, rawatobs=None, ix=None):
        """
        Return the field of *raw* values adjusted by *obs*.

        Parameters
        ----------
        obs : array of floats
            Gage observations
        raw : array of floats
            Raw unadjusted radar rainfall
        targets : (INTERNAL) array of floats
            Coordinate pairs for locations on which the final adjustment product is interpolated
            Defaults to None. In this case, the output locations will be identical to the radar coordinates
        rawatobs : (INTERNAL) array of floats
            For internal use from AdjustBase.xvalidate only (defaults to None)
        ix : (INTERNAL) array of integers
            For internal use from AdjustBase.xvalidate only (defaults to None)

        """
        # ----------------GENERIC PART FOR MOST __call__ methods----------------
        if None in [ix, rawatobs]:
            # Check for valid observation-radar pairs in case this method has not been called from self.xvalidate
            rawatobs, ix = self._get_valid_pairs(obs, raw)
        if len(ix)<=self.mingages:
            # Not enough valid gages for adjustment? - return unadjusted data
            return raw
        # Get new Interpolator instance if necessary
        ip = self._checkip(ix, targets)

        # -----------------THIS IS THE ACTUAL ADJUSTMENT APPROACH---------------
        # interpolate gage observations
        return ip(obs[ix])



class Raw_at_obs():
    """
    Get the raw values in the neighbourhood of the observation points

    Parameters
    ----------
    obs_coords : array of float
        coordinate pairs of observations points
    raw_coords : array of float
        coordinate pairs of raw (unadjusted) field
    nnear: integer
        number of neighbours which should be considered in the vicinity of each point in obs
    stat: string
        function name

    """
    def __init__(self, obs_coords, raw_coords, nnear=9, stat='median'):
        self.statfunc = _get_statfunc(stat)
        self.raw_ix = _get_neighbours_ix(obs_coords, raw_coords, nnear)

    def __call__(self, raw, obs=None):
        """
        Returns the values of raw at the observation locations

        Parameters
        ----------
        raw : array of float
            raw values

        """
        # get the values of the raw neighbours of obs
        raw_neighbs = raw[self.raw_ix]
        # and summarize the values of these neighbours by using a statistics option
        # (only needed in case nnear > 1, i.e. multiple neighnours per observation location)
        if raw_neighbs.ndim > 1:
            return self.statfunc(obs, raw_neighbs)
        else:
            return raw_neighbs


def _get_neighbours_ix(obs_coords, raw_coords, nnear):
    """
    Returns <nnear> neighbour indices per <obs_coords> coordinate pair

    Parameters
    ----------
    obs_coords : array of float of shape (num_points,ndim)
        in the neighbourhood of these coordinate pairs we look for neighbours
    raw_coords : array of float of shape (num_points,ndim)
        from these coordinate pairs the neighbours are selected
    nnear : integer
        number of neighbours to be selected per coordinate pair of obs_coords

    """
    # plant a tree
    tree = cKDTree(raw_coords)
    # return nearest neighbour indices
    return tree.query(obs_coords, k=nnear)[1]


def _get_neighbours(obs_coords, raw_coords, raw, nnear):
    """
    Returns <nnear> neighbour values per <obs_coords> coordinate pair

    Parameters
    ----------
    obs_coords : array of float of shape (num_points,ndim)
        in the neighbourhood of these coordinate pairs we look for neighbours
    raw_coords : array of float of shape (num_points,ndim)
        from these coordinate pairs the neighbours are selected
    raw : array of float of shape (num_points,...)
        this is the data corresponding to the coordinate pairs raw_coords
    nnear : integer
        number of neighbours to be selected per coordinate pair of obs_coords

    """
    # plant a tree
    tree = cKDTree(raw_coords)
    # retrieve nearest neighbour indices
    ix = tree.query(obs_coords, k=nnear)[1]
    # return the values of the nearest neighbours
    return raw[ix]


def _get_statfunc(funcname):
    """
    Returns a function that corresponds to parameter <funcname>

    Parameters
    ----------
    funcname : string
        a name of a numpy function OR another option known by _get_statfunc
        Potential options: 'mean', 'median', 'best'

    """
    try:
        # first try to find a numpy function which corresponds to <funcname>
        func = getattr(np,funcname)
        def newfunc(x, y):
            return func(y, axis=1)
    except:
        try:
            # then try to find a function in this module with name funcname
            if funcname=='best':
                newfunc=best
        except:
            # if no function can be found, raise an Exception
            raise NameError('Unkown function name option: '+funcname)
    return newfunc


def best(x, y):
    """
    Find the values of y which corresponds best to x

    If x is an array, the comparison is carried out for each element of x

    Parameters
    ----------
    x : float or 1-d array of float
    y : array of float

    Returns
    -------
    output : 1-d array of float with length len(y)

    """
    if type(x)==np.ndarray:
        assert x.ndim==1, 'x must be a 1-d array of floats or a float.'
        assert len(x)==len(y), 'Length of x and y must be equal.'
    if type(y)==np.ndarray:
        assert y.ndim<=2, 'y must be 1-d or 2-d array of floats.'
    else:
        raise ValueError('y must be 1-d or 2-d array of floats.')
    x = np.array(x).reshape((-1,1))
    if y.ndim==1:
        y = np.array(y).reshape((1,-1))
        axis = None
    else:
        axis = 1
    return y[np.arange(len(y)),np.argmin(np.abs(x-y), axis=axis)]


def get_raw_at_obs(obs_coords, raw_coords, obs, raw, nnear=9, stat='median'):
    """
    Get the raw values in the neighbourhood of the observation points

    Parameters
    ----------

    obs_coords :

    raw: Datset of raw values (which shall be adjusted by obs)
    nnear: number of neighbours which should be considered in the vicinity of each point in obs
    stat: a numpy statistical function which should be used to summarize the values of raw in the neighbourshood of obs

    """
    # get the values of the raw neighbours of obs
    raw_neighbs = _get_neighbours(obs_coords, raw_coords, raw, nnear)
    # and summarize the values of these neighbours by using a statistics option
    return _get_statfunc(stat)(raw_neighbs)




if __name__ == '__main__':
    print 'wradlib: Calling module <adjust> as main...'
