import os
import mdtraj


def test_1():
    capi = mdtraj.capi()
    assert os.path.isdir(capi['lib_dir'])
    assert os.path.isdir(capi['include_dir'])
    assert os.path.isfile(os.path.join(capi['lib_dir'], 'libtheobald.a'))
