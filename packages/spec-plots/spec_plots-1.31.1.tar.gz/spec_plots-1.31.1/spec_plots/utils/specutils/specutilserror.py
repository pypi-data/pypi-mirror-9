__version__ = '1.31.1'

"""
.. module:: specutilserror

   :synopsis: Defines a custom Error class for use with spec_plots utility functions.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

#--------------------
class SpecUtilsError(Exception, object):
    """
    This class defines a generic Exception to use for errors raised in the SPECUTILS modules (specutils, specutils_cos, specutils_stis, etc.).  It simply prints the given value when raising the exception, e.g., 
    
    .. code-block:: python
    
         raise SpecUtilsError("Print this string") 
         SpecUtilsError: *** SPECUTILS ERROR: 'Print this string'
    """

    def __init__(self, value):
        """
        Initiate the Exception.

        :param value: The string to print on error.

        :type value: str
        """
        self.value = value

    def __str__(self):
        """
        Overrides the str function for this class.
        """
        return "*** SPECUTILS ERROR: "+repr(self.value)
#--------------------
