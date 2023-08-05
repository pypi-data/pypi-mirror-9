Salvage distributes sensitive data to multiple people such that it can only be
recovered by several people working together. This is useful for storing
information with both a low risk of losing access to it and a low risk of
accidental exposure. A classic application is to create a "recovery kit" for a
server or infrastructure, which can be used in the event that conventionally
stored keys and credentials become lost or unavailable.

Salvage works by encrypting a file or directory with a random master key and
then applying a simple key-splitting scheme to distribute the key across
multiple shares. You can create a kit for any number of participants with any
threshold required to recover the information. For example, you might create a
kit for five people, any three of whom may combine their shares to recover the
data.

Salvage runs under Python 2.7 or Python 3.2 and later. The only external
dependency is `gpg`_, for the cryptography. For maximum utility, it is packaged
as a single flat Python script that can be run with no installation. The
algorithms and file formats are simple and carefully documented to ensure that
recovery is always possible even if this software is unavailable for some
reason.


Installation
------------

    ``$ pip install salvage``

This package will only install the ``salvage`` executable. It does not depend on
any Python packages.


Quick Start
-----------

To create a new salvage kit for five participants with a recovery threshold of
three:

    ``% salvage new 5 3 path/to/source/dir``

This will create five shares, each containing an encrypted archive and some
metadata. To decrypt and unpack the archive:

    ``% salvage recover path/to/share1 path/to/share2 path/to/share3``

The three paths must be three of the shares generated in the first step. The
master key will be reconstructed and the data will be decrypted and unpacked.

See ``salvage -h`` for additional options.


.. _gpg: https://www.gnupg.org/
