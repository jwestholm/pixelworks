#!/usr/bin/env python3
"""Pixel Works – single stable launcher.

Use the v0.12.0.9 checked-in engine from this application's local Git checkout,
then attach separately versioned features. No network calls or migrations at boot.
Note: this compatibility launcher requires the original dev Git history. It fails
closed, without writing user files, if the engine blob is not present locally.
"""
import hashlib
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL_SHA = '1abf4bdd611ba543d73f79f6b7f79be28f777899'


def load_base():
    if not (ROOT / '.git').exists():
        raise RuntimeError('Pixel Works behöver den lokala Git-klonen av dev för denna delta-version. Originalservern ändras inte automatiskt.')
    command = ['git', '-C', str(ROOT), 'cat-file', 'blob', ORIGINAL_SHA]
    result = subprocess.run(command, capture_output=True, timeout=12, check=False)
    if result.returncode:
        raise RuntimeError('Originalmotorn v0.12.0.9 saknas i din lokala Git-historik. Ingen start utfördes.')
    raw = result.stdout
    object_sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if object_sha != ORIGINAL_SHA:
        raise RuntimeError('Originalmotorns Git-hash matchar inte. Start stoppad utan filändringar.')
    base = types.ModuleType('pixelworks_core')
    base.__file__ = str(ROOT / 'backend' / 'server.py')
    base.__package__ = ''
    sys.modules['pixelworks_core'] = base
    exec(compile(raw, base.__file__, 'exec'), base.__dict__)
    return base


def main():
    core = load_base()
    from pw_v01210 import install
    install(core)
    # Delta: extend the already-installed real cafe discussion with safe images.
    from pw_cafe_images import install as install_cafe_images
    install_cafe_images(core)
    return core.main()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print('Pixel Works kunde inte starta: ' + str(error), file=sys.stderr)
        sys.exit(1)
