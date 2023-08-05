monkeytime
==========

Patch datetime to use a much quicker strptime implementation.

This **ONLY** improves strptime when the format string uses padded directives.

This is the list of supported directives (by far the most common)::

    SUPPORTED_DIRECTIVES = ('%d', '%m', '%Y', '%H', '%M', '%S', '%f')

Check if your date/time format is supported by calling::
    
    datetime.supported_strptime(format_string)
    # True if supported, False otherwise

On average, 4 times quicker than the stdlib version, and 50 times as quick
when using pypy!

Usage::

    # insert this one line
    from monkeytime import datetime
    # Done migrating code to monkeytime!

    from datetime import datetime

    # Call it once with the specific format string
    # It will build a new function to quickly parse the string, then run it on
    # the string you passed it.
    dt = datetime.strptime('2014-05-30T12:14:15.123456', '%Y-%m-%dT%H:%M:%S.%f')
    
    # Now, whenever you use that format again, it will use the function it 
    # built already! All constructed functions are memoized.
    # Since we usually only use one or two formats in our code to parse logs
    # and such, the performance of constructing it is negligible.

All you need is that one line "from monkeytime import datetime", and your
strptime performance will increase dramatically. 

**Make sure it is ABOVE your "from datetime import datetime" import line!**
