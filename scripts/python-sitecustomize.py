"""Local sandbox compatibility tweaks for the workspace Python."""

import os


if os.name == "nt":
    import errno as _errno
    import sys as _sys
    import tempfile as _tempfile

    def _mkdtemp_world_accessible(suffix=None, prefix=None, dir=None):
        """Create temp directories with ACLs usable by this sandbox."""

        prefix, suffix, dir, output_type = _tempfile._sanitize_params(
            prefix, suffix, dir
        )

        names = _tempfile._get_candidate_names()
        if output_type is bytes:
            names = map(os.fsencode, names)

        for _ in range(_tempfile.TMP_MAX):
            name = next(names)
            file = os.path.join(dir, prefix + name + suffix)
            _sys.audit("tempfile.mkdtemp", file)
            try:
                os.mkdir(file, 0o777)
            except FileExistsError:
                continue
            except PermissionError:
                if os.path.isdir(dir) and os.access(dir, os.W_OK):
                    continue
                raise
            return os.path.abspath(file)

        raise FileExistsError(
            _errno.EEXIST, "No usable temporary directory name found"
        )

    _tempfile.mkdtemp = _mkdtemp_world_accessible
