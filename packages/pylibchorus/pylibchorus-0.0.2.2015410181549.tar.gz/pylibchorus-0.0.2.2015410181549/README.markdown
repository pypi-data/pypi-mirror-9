# pylibchorus -- Python Chorus API Library #

[![Build Status](https://travis-ci.org/kennyballou/pylibchorus.svg)](https://travis-ci.org/kennyballou/pylibchorus)

This intends to be a near complete Python language binding of the
[Chorus API][1].

The library itself will likely be very unstable for a little while as
its development progresses.

## Sample Usage ##

Here is a sample interactive session that demonstrates the current
usage.

    >>> import pylibchorus
    >>> from ConfigParser import SafeConfigParser
    >>> config = SafeConfigParser()
    >>> config.read('/tmp/alpine.cfg')
    ['/tmp/alpine.cfg']
    >>> with pylibchorus.ChorusSession(config) as session:
    ...     print(session.sid)
    ...     resp = pylibchorus.check_login_status(session)
    ...     print(resp.status_code)
    ...     json = resp.json()
    ...     print(json['response']['session_id'])
    ...
    49fb8e27e591d9ccb6f0006334eedb8e4d8004a5
    200
    49fb8e27e591d9ccb6f0006334eedb8e4d8004a5
    >> quit()

Notice, some of the interactions that depend on the `requests`
library may be cleaned up in the future, enabling easier interaction
with this library.

## License ##

This code is licensed and distributed, as-is without warranty and in
the hopes it will be useful under the terms and conditions of the MIT
license. Please see the LICENSE file for more information. If the
LICENSE file was not distributed with your copy, you may also find it
[on the web][2].

[1]: https://github.com/chorus/chorus

[2]: http://opensource.org/licenses/MIT

<!--- vim: colorcolumn=70:textwidth=69:
-->
