# Copyright 2009-2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

# Make this directory into a Python package.

import os


def get_txpkgupload_root(fsroot):
    """Return the txpkgupload root to use for this server.

    If the TXPKGUPLOAD_ROOT environment variable is set, use that. If not,
    use fsroot.
    """
    txpkgupload_root = os.environ.get('TXPKGUPLOAD_ROOT', None)
    if txpkgupload_root:
        return txpkgupload_root
    return fsroot
