"""v3.5.2: narrowly allowlist the v3.5 CSS and v3 character sprite assets.

The original core serves /src/*.js and /assets/office-v2/* but not the
newer stylesheet/sprite paths. Do not expose arbitrary local project files.
"""
import re
from pathlib import Path
from urllib.parse import urlparse

_STYLES=frozenset({
    '/src/pw-v35-world.css',
    '/src/pw-v351-dialogs.css',
    '/src/pw-v352-personnel.css',
    '/src/pw-v353-office.css',
})
_CHARACTER=re.compile(r'^/assets/characters/(chef|joppe|siv|nisse|mira|vera|lova)/\1-(idle|walk|working|cafe|talk|celebrate)\.png$')


def install(srv):
    if getattr(srv,'_PW_V352_STATIC',False):
        return
    srv._PW_V352_STATIC=True
    old_get=srv.Handler.do_GET

    def do_GET(self):
        route=urlparse(self.path).path
        if route not in _STYLES and not _CHARACTER.fullmatch(route):
            return old_get(self)
        if not self.allowed():
            return self.reply(403,{'error':'Otillåten värdadress'})
        root=Path(srv.APP).resolve()
        f=root/route.lstrip('/')
        # Explicit file type + path allowlist, and do not follow symlinks.
        if (not f.is_file() or f.is_symlink() or f.parent.is_symlink()
                or f.parent.parent.is_symlink() or not f.resolve().is_relative_to(root)):
            return self.reply(404,{'error':'Statisk resurs saknas'})
        # Keep core's nosniff, CSP, no-store and MIME handling. No API routes
        # or protected files are served through this branch.
        return srv.SimpleHTTPRequestHandler.do_GET(self)

    srv.Handler.do_GET=do_GET
