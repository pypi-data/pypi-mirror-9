__version__ = '1.31.2'

"""
.. module:: edge_trim

   :synopsis: Returns the start and end indices of a spectrum that represent the `best` wavelengths to use when defining the optimal plot axis ranges.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import numpy
from is_bad_dq import is_bad_dq

#--------------------
def _set_plot_xrange_test(instrument, flux_values, flux_err_values, median_flux, flux_scale_factor, median_fluxerr, fluxerr_scale_factor, fluxerr_95th, dqs, checkFluxes=False, checkFluxRatios=False, checkFluxErrRatios=False, checkFluxErrPercentile=False, checkDQs=False):
    """
    Defines the test for an invalid part of the spectrum when trimming from the edges along the wavelength (x) axis.

    :param instrument: The instrument that is being tested.

    :type instrument: str

    :param flux_values: An array of fluxes to test.

    :type flux_values: numpy.ndarray

    :param flux_err_values: An array of associated flux uncertainties.

    :type flux_err_values: numpy.ndarray

    :param median_flux: A median flux value, used in the test.

    :type median_flux: float

    :param flux_scale_factor: Max. allowed ratio between the flux and a median flux value, used in edge trimming.

    :type flux_scale_factor: float

    :param median_fluxerr: A median flux uncertainty value, used in the test.

    :type median_fluxerr: float

    :param fluxerr_scale_factor: Max. allowed ratio between the flux uncertainty and a median flux uncertainty value, used in edge trimming.

    :type fluxerr_scale_factor: float

    :param fluxerr_95th: The flux uncertainty corresponding to the 95th percentile.

    :type fluxerr_95th: float

    :param dqs: The array of DQ flags to use in the test.  For COS, these are the DQ_WGT bits from the header.

    :type dqs: numpy.ndarray

    :param checkFluxes: Should the value of the fluxes be used to test edge trimming?

    :type checkFluxes: bool

    :param checkFluxRatios: Should the ratio of the fluxes to the median flux value be used to test edge trimming?

    :type checkFluxRatios: bool

    :param checkFluxErrRatios: Should the ratio of the flux uncertainties to the median flux uncertainty be used to test edge trimming?

    :type checkFluxErrRatios: bool

    :param checkFluxErrPercentile: Should the highest percentile flux uncertainties be used to test edge trimming?

    :type checkFluxErrPercentile: bool

    :param checkDQs: Should the highest percentile flux uncertainties be used to test edge trimming?

    :type checkDQs: bool

    :returns: list -- A list of True/False values depening on whether the input flux values pass the test.  Note that if a return value is True, then the flux value is considered PART OF THE SPECTRUM TO KEEP.  If median_flux is input as NaN, then this function returns False for all flux_values (i.e., skip all of them since median_flux is not defined).

    :raises: ValueError
    """
    
    """ Make sure input parameters are all numpy arrays. """
    if not isinstance(flux_values, numpy.ndarray) or not isinstance(flux_err_values, numpy.ndarray) or not isinstance(dqs, numpy.ndarray):
        raise ValueError("The flux, flux uncertainty, and DQ values must be passed as a numpy.ndarray object.")

    """ Return array of boolean values for the edge_trim test. """
    if numpy.isfinite(median_flux):
        bool_results = [ ( (instrument == "cos" and x != 0. and checkFluxes) or (instrument == "stis" and x != 0. and checkFluxes) or (not checkFluxes) ) \
                             and ( (abs(x/median_flux) < flux_scale_factor and checkFluxRatios) or (not checkFluxRatios) ) \
                             and ( (y/median_fluxerr < fluxerr_scale_factor and checkFluxErrRatios) or (not checkFluxErrRatios) ) \
                             and ( (y <= fluxerr_95th and checkFluxErrPercentile) or (not checkFluxErrPercentile) ) \
                             and ( (instrument == "stis" and not is_bad_dq(instrument, z) and checkDQs) or (instrument == "cos" and not is_bad_dq(instrument, z) and checkDQs) or (not checkDQs) ) \
                             for x,y,z in zip(flux_values, flux_err_values, dqs) ]
    else:
        bool_results = [False] * len(flux_values)

    return bool_results
#--------------------

#--------------------
def edge_trim(instrument, fluxes, fluxerrs, dqs, n_consecutive, median_flux, flux_scale_factor, median_fluxerr, fluxerr_scale_factor, fluxerr_95th):
    """
    Returns start and end indexes (end indexes are negatively indexed) of the best part of the spectrum to use when defining the plot's wavelength ranges.  Returns two sets of start and end indexes: one set without taking into account DQ flags, and one set that does take into account DQ flags (since some spectra have all DQ flags set > 0).

    :param instrument: The instrument that is being tested.

    :type instrument: str

    :param fluxes: The fluxes to be plotted.

    :type fluxes: numpy.ndarray

    :param fluxerrs: The uncertainties of the fluxes to be plotted.

    :type fluxerrs: numpy.ndarray

    :param dqs: The DQ flags of the spectrum.  For COS, these are the DQ_WGT bits from the header.

    :type dqs: numpy.ndarray

    :param n_consecutive: The consecutive number of fluxes that must belong to the "best" part of the spectrum for the start/end index to count.

    :type n_consecutive: int

    :param median_flux: The median flux, used in determining where the best part of the spectrum is.

    :type median_flux: float

    :param flux_scale_factor: Max. allowed ratio between the flux and a median flux value, used in edge trimming.

    :type flux_scale_factor: float

    :param median_fluxerr: The median flux uncertainty, used in determining where the best part of the spectrum is.

    :type median_fluxerr: float

    :param fluxerr_scale_factor: Max. allowed ratio between the flux uncertainty and a median flux uncertainty value, used in edge trimming.

    :type fluxerr_scale_factor: float

    :param fluxerr_95th: The flux uncertainty corresponding to the 95th percentile.

    :type fluxerr_95th: float

    :returns: int tuple -- Indexes that define the best part of the spectrum, in the order of (start_index_nodq, end_index_nodq, start_index_withdq, end_index_withdq).
    """

    n_fluxes = len(fluxes)

    """ Determine the indices where each flux point satisfies our test criteria, ignoring DQ values. """
    where_good_fluxes_nodq = numpy.where(numpy.asarray(_set_plot_xrange_test(instrument, fluxes, fluxerrs, median_flux, flux_scale_factor, median_fluxerr, fluxerr_scale_factor, fluxerr_95th, dqs, checkFluxes=True, checkFluxRatios=False, checkFluxErrRatios=True, checkFluxErrPercentile=False, checkDQs=False)))[0]
    n_good_fluxes_nodq = len(where_good_fluxes_nodq)

    """ Handle the trivial case where the number of valid points is less than the `n_consecutive` desired.  In this case, the start and end indices are set to the last and first indices, simulating what would happen if the entire array was traversed. """
    if n_good_fluxes_nodq < n_consecutive:
        start_index_nodq = 0
        end_index_nodq = -1
    else:
        """ The start index is then the min. index for which the `n_consecutive`'th index is exactly equal to `n_consecutive`-1. """
        start_indexes_nodq_with_good_diffs = numpy.asarray([x for i,x in enumerate(where_good_fluxes_nodq[0:n_good_fluxes_nodq-n_consecutive+1]) \
                                                                if where_good_fluxes_nodq[i+n_consecutive-1] - \
                                                                where_good_fluxes_nodq[i] == n_consecutive-1])

        if len(start_indexes_nodq_with_good_diffs) > 0:
            start_index_nodq = numpy.min(start_indexes_nodq_with_good_diffs)
            end_index_nodq = numpy.max(start_indexes_nodq_with_good_diffs) - n_fluxes + n_consecutive - 1
        else:
            start_index_nodq = 0
            end_index_nodq = -1

    """ Determine the indices where each flux point satisfies our test criteria, taking into account DQ values. """
    where_good_fluxes_withdq = numpy.where(numpy.asarray(_set_plot_xrange_test(instrument, fluxes, fluxerrs, median_flux, flux_scale_factor, median_fluxerr, fluxerr_scale_factor, fluxerr_95th, dqs, checkFluxes=True, checkFluxRatios=False, checkFluxErrRatios=True, checkFluxErrPercentile=False, checkDQs=True)))[0]
    n_good_fluxes_withdq = len(where_good_fluxes_withdq)

    """ Handle the trivial case where the number of valid points is less than the `n_consecutive` desired.  In this case, the start and end indices are set to the last and first indices, simulating what would happen if the entire array was traversed. """
    if n_good_fluxes_withdq < n_consecutive:
        start_index_withdq = 0
        end_index_withdq = -1
    else:
        """ The start index is then the min. index for which the `n_consecutive`'th index is exactly equal to `n_consecutive`-1. """
        start_indexes_withdq_with_good_diffs = numpy.asarray([x for i,x in enumerate(where_good_fluxes_withdq[0:n_good_fluxes_withdq-n_consecutive+1]) \
                                                                if where_good_fluxes_withdq[i+n_consecutive-1] - \
                                                                where_good_fluxes_withdq[i] == n_consecutive-1])
        if len(start_indexes_withdq_with_good_diffs) > 0:
            start_index_withdq = numpy.min(start_indexes_withdq_with_good_diffs)
            end_index_withdq = numpy.max(start_indexes_withdq_with_good_diffs) - n_fluxes + n_consecutive - 1
        else:
            start_index_withdq = 0
            end_index_withdq = -1

    return start_index_nodq, end_index_nodq, start_index_withdq, end_index_withdq
#--------------------
