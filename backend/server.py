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
    # AI employee audio tool; no network calls or migrations at startup.
    from pw_freesound import install as install_freesound
    install_freesound(core)
    # Tool calls stay backend-owned; integrated work queues passive QA handoff.
    from pw_tool_registry import install as install_tools
    install_tools(core)
    from pw_qa_handoff import install as install_qa
    install_qa(core)
    # Unified, player-owned approval inbox for actual images and sound previews.
    from pw_media_review import install as install_media_review
    install_media_review(core)
    # One decision center for existing help cases, asset approvals and bounded retries.
    from pw_decision_center import install as install_decision_center
    install_decision_center(core)
    # Optional, password-protected home-LAN access, disabled by default.
    # Explicit, recoverable global staff inventory. No startup migration.
    from pw_global_staff_v25 import install as install_global_staff
    install_global_staff(core)
    # Opt-in cutover: global workforce is authoritative only after explicit player approval.
    from pw_global_workforce_v27 import install as install_global_workforce
    install_global_workforce(core)
    # V3 recruitment prototype – old worker types remain, old schedulers pause after owner opt-in.
    from pw_recruitment_v3 import install as install_recruitment_v3
    install_recruitment_v3(core)
    # v3.3: real, manual AI tasks with immutable personas and review before integration.
    from pw_v3_jobs import install as install_v3_jobs
    install_v3_jobs(core)
    # v3.4: Chief suggests crew from real availability + fictional skills, never auto-runs AI.
    from pw_v3_chief import install as install_v3_chief
    install_v3_chief(core)
    # v3.5.2: permit ONLY the named new CSS and seven character sprite atlases.
    # Original core already sends Cache-Control: no-store.
    from pw_v352_static import install as install_v352_static
    install_v352_static(core)
    # Keep the LAN access guard as the outermost HTTP wrapper.
    from pw_lan import install as install_lan
    install_lan(core)
    return core.main()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print('Pixel Works kunde inte starta: ' + str(error), file=sys.stderr)
        sys.exit(1)
