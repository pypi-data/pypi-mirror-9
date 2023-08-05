monkeytime
==========

Patch datetime to use a much quicker strptime implementation.

This **ONLY** improves strptime when the format string uses padded directives.

This is the list of supported directives (by far the most common)::

    SUPPORTED_DIRECTIVES = ('%d', '%m', '%Y', '%H', '%M', '%S', '%f')

Check if your date/time format is supported by calling::
    
    datetime.supported_strptime(format_string)
    # True if supported, False otherwise

On average, 4 times quicker than the stdlib version, and 40 times quicker
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

Performance example::

    $ python timeit_test.py 
    Testing builtin strptime
    testing ('2015-01-02 03:04:05.001234', '%Y-%m-%d %H:%M:%S.%f')
    6.80288290977 seconds
    testing ('05-06 12:15:18', '%m-%d %H:%M:%S')
    5.81049013138 seconds
    testing ('2010', '%Y')
    4.29107117653 seconds
    testing ('1905/08/05', '%Y/%m/%d')
    4.92634987831 seconds
    testing ('14:05:03.123456', '%H:%M:%S.%f')
    5.6812889576 seconds
    Testing monkeytime strptime
    testing ('2015-01-02 03:04:05.001234', '%Y-%m-%d %H:%M:%S.%f')
    1.83126211166 seconds
    testing ('05-06 12:15:18', '%m-%d %H:%M:%S')
    1.5586848259 seconds
    testing ('2010', '%Y')
    0.877351999283 seconds
    testing ('1905/08/05', '%Y/%m/%d')
    1.24154901505 seconds
    testing ('14:05:03.123456', '%H:%M:%S.%f')
    1.3871409893 seconds
    3.714860 times as fast
    3.727816 times as fast
    4.890935 times as fast
    3.967906 times as fast
    4.095682 times as fast
    Average: 4.079440 times as fast

    $ pypy timeit_test.py 
    Testing builtin strptime
    testing ('2015-01-02 03:04:05.001234', '%Y-%m-%d %H:%M:%S.%f')
    2.19319605827 seconds
    testing ('05-06 12:15:18', '%m-%d %H:%M:%S')
    1.60669994354 seconds
    testing ('2010', '%Y')
    0.858637809753 seconds
    testing ('1905/08/05', '%Y/%m/%d')
    1.19449591637 seconds
    testing ('14:05:03.123456', '%H:%M:%S.%f')
    1.38721394539 seconds
    Testing monkeytime strptime
    testing ('2015-01-02 03:04:05.001234', '%Y-%m-%d %H:%M:%S.%f')
    0.0362730026245 seconds
    testing ('05-06 12:15:18', '%m-%d %H:%M:%S')
    0.0450730323792 seconds
    testing ('2010', '%Y')
    0.0332229137421 seconds
    testing ('1905/08/05', '%Y/%m/%d')
    0.0321681499481 seconds
    testing ('14:05:03.123456', '%H:%M:%S.%f')
    0.0355319976807 seconds
    60.463593 times as fast
    35.646591 times as fast
    25.844747 times as fast
    37.132876 times as fast
    39.041260 times as fast
    Average: 39.625813 times as fast

