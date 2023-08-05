import time
import calendar
import struct
import base64


def generate_uid(yr=None):
  
    """
    Makes an id that is unique to within one microsecond of calling
    this function for the execution context which runs this method.
    
    This is a simple, fast id generator that is adequate for most
    purposes.
    
    The base year parameter should be no greater than the current
    year and should not change over the lifetime of all objects
    created using that year. A higher base year results in a smaller
    UID.
    
    :param: the optional base year for the time offset (default 2001)
    :rtype: long
    :return: the UID
    """
    # The default year.
    if not yr:
      yr = 2001
    # A starting time prior to now.
    start = time.mktime(calendar.datetime.date(yr, 01, 01).timetuple())
    # A long which is unique to within one microsecond.
    return long((time.time() - start) * 1000000)


def generate_string_uid(yr=None):
    """
    Makes a string id based on the :meth:`generate_uid` value.
    The string id is a URL-safe base64-encoded string without trailing
    filler or linebreak. It is thus suitable for file names as well as
    URLs.
    
    The generated id is ten characters long for the default base year.
    
    :param yr: the optional :meth:`generate_uid` base year parameter
    :rtype: str
    :return: the UID
    """
    # The long uid.
    uid = generate_uid(yr)
    # Encode the long uid without trailing filler or linebreak.
    return base64.urlsafe_b64encode(struct.pack('L', uid)).rstrip('A=\n')
