Python TBX - Toolbox Library
============================


About
-----

Python Toolbox aka TBX is a collection of very different tools created over the years to simplify my coding.
As a library, this has no purpose by itself and should be used by other projects.

Project url : https://github.com/ronhanson/python-tbx


Description
-----------

The library contains several unrelated tool collections :


- **tbx.bytes** - Byte manipulation

    *Allows encoding and decoding of various formats.*

- **tbx.code** - Useful coding tools

    *Singleton, method documentation parsing, module lazy-load, serializable object, etc.*

- **tbx.file** - File manipulation

    *Recursive file listing, linux based unzip/untar/etc.*

- **tbx.ftp** - FTP Server helpers

    *Server creation helpers, event handlers. Based on awesome pyftpdlib.*

- **tbx.log** - Logging helpers

    *Helps with logging configuration from settings file.*

- **tbx.network** - Network helpers

    *Provides a dummy socket client and a get_local_ip_address function.*

- **tbx.process** - Multiprocessing helpers

    *Provides a versatile "execute" function, but also a daemonize function, and some more.*

- **tbx.sequential** - File sequence detection

    *Provides useful detection of file sequence.*

- **tbx.service** - Service helpers

    *A class allowing to build a small loop-based service in no time.*

- **tbx.settings** - Settings helpers

    *Allows to easily retrieve and validate settings file.*

- **tbx.snmp** - SNMP helpers

    *Small helper to send a snmp request throught pysnmp.*

- **template** - Templating helpers

    *Provides useful helpers for Jinja templating system.*

- **tbx.text** - Text manipulation tools

    *Includes dict to XML/HTML/Text functions. Provides a simple sendmail method and miscellaneous text related methods.*

- **tbx.env_settings** - Environment based settings

    *Deprecated*


Usage
-----

Just look at the code as it is commented for your to understand its usage.

No big doc made yet. This is more of a personal collection of snippets and tools.

But if somebody is interested or requests it, I will make a better doc.


Compatibility
-------------

This libraries are used most on Linux and OSX systems, but plenty of functions may work on windows.

This libraries are compatibles with Python 2.X and Python 3.X.

Mainly tested on 2.7 and 3.4.


Author & Licence
----------------

Copyright (c) 2010-2015 Ronan Delacroix

This program is released under MIT Licence. Feel free to use it or part of it anywhere you want.