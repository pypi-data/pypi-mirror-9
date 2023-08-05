__version__ = '1.31.2'

"""
.. module:: avoidregion

   :synopsis: Create AvoidRegions in wavelength space that will not be used when determining the optimal y-axis plot rangex.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------
class AvoidRegion(object):
    """
    Defines an avoid region, which is a section of wavelength space that should not be included when determining the optimal y-axis plot range.  The object consists of a starting wavelength, ending wavelength, and string description of what that region is.

    :raises: ValueError
    """
    def __init__(self, minwl=None, maxwl=None, description=""):

        if minwl is None:
            raise ValueError("Must specify a minimum wavelength for this avoid region.")

        if maxwl is None:
            raise ValueError("Must specify a maximum wavelength for this avoid region.")

        if minwl >= maxwl:
            raise ValueError("Minimum wavelength must be less than maximum wavelength for this avoid region.  Given min. wavelength = "+str(minwl)+" and max. wavelength = "+str(maxwl)+".")

        """ Assign the min. wl., max. wl., and description to the object. """
        self.minwl = minwl
        self.maxwl = maxwl
        self.description = description
#--------------------


#--------------------
def generate_avoid_regions(instrument):
    """
    Creates a list of AvoidRegion objects for use in the plotting routine, specifically designed for the given instrument.

    :param instrument: The instrument to generate the Avoid Region for.

    :type instrument: str

    """

    if instrument == "cos":
        lya1215_ar = AvoidRegion(1214.,1217., "Lyman alpha emission line.")
        return [lya1215_ar]

    elif instrument == "stis":
        lya1215_ar = AvoidRegion(1214.,1217., "Lyman alpha emission line.")
        return [lya1215_ar]

    else:
        return []
#--------------------
