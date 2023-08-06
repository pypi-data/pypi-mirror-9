Rally Style Commandments
========================

- Step 1: Read the OpenStack Style Commandments
  http://docs.openstack.org/developer/hacking/
- Step 2: Read on

Rally Specific Commandments
---------------------------
* [N30x] - Reserved for rules related to ``mock`` library
 * [N301] - Ensure that ``assert_*`` methods from ``mock`` library is used correctly
 * [N302] - Ensure that nonexistent "assert_called" is not used
 * [N303] - Ensure that  nonexistent "assert_called_once" is not used
* [N310-N314] - Reserved for rules related to logging
 * [N310] - Ensure that ``rally.common.log`` is used as logging module
 * [N311] - Validate that debug level logs are not translated
 * [N312] - Validate correctness of debug on check.
* [N32x] - Reserved for rules related to assert* methods
 * [N320] - Ensure that ``assertTrue(isinstance(A, B))``  is not used
 * [N321] - Ensure that ``assertEqual(type(A), B)`` is not used
 * [N322] - Ensure that ``assertEqual(A, None)`` and ``assertEqual(None, A)`` are not used
 * [N323] - Ensure that ``assertTrue/assertFalse(A in/not in B)`` are not used with collection contents
 * [N324] - Ensure that ``assertEqual(A in/not in B, True/False)`` and ``assertEqual(True/False, A in/not in B)`` are not used with collection contents
* [N33x] - Reserved for rules related to Python 3 compatibility
 * [N330] - Ensure that ``dict.iterkeys()``, ``dict.itervalues()``, ``dict.iteritems()`` and ``dict.iterlist()`` are not used
 * [N331] - Ensure that ``basestring`` is not used
 * [N332] - Ensure that ``StringIO.StringIO`` is not used
 * [N333] - Ensure that ``urlparse`` is not used
 * [N334] - Ensure that ``itertools.imap`` is not used
 * [N335] - Ensure that ``xrange`` is not used
 * [N336] - Ensure that ``string.lowercase`` and ``string.uppercase`` are not used
 * [N337] - Ensure that ``next()`` method on iterator objects is not used
 * [N338] - Ensure that ``+`` operand is not used to concatenate dict.items()
* [N340] - Ensure that we are importing always ``from rally import objects``
* [N341] - Ensure that we are importing oslo_xyz packages instead of deprecated oslo.xyz ones