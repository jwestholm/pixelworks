"""Pixel Works: backend-owned registry for employee tools (v0.14-toolbridge).

Providers are employees, tools are operations. Only the backend dispatches tool
operations; no API secret or arbitrary command is exposed to Codex/Gemini or JS.
The registry deliberately has one real adapter today; other integrations are
not advertised as installed until they have an implementation and permissions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


@dataclass(frozen=True)
class Tool:
    ident: str
    label: str
    station_ids: tuple[str, ...]
    operations: tuple[str, ...]
    availability: object  # (srv) -> (connected, verified)
    execute: object       # (srv, slug, operation, arguments) -> real result


class Registry:
    def __init__(self, server):
        self.server = server
        self.tools: dict[str, Tool] = {}

    def register(self, tool):
        if tool.ident in self.tools or not re.fullmatch(r'[a-z][a-z0-9_-]{1,40}', tool.ident):
            raise ValueError('Verktygs-ID finns redan eller är ogiltigt')
        self.tools[tool.ident] = tool

    def list(self, slug=None, agent=None):
        if slug is not None:
            slug = self.server.validate_slug(slug)
            self.server.verify_project(slug)
        items = []
        for tool in self.tools.values():
            connected, verified = tool.availability(self.server)
            if agent is not None and agent.get('station') not in tool.station_ids:
                continue
            items.append({'id': tool.ident, 'label': tool.label,
                          'operations': list(tool.operations), 'stations': list(tool.station_ids),
                          'connected': bool(connected), 'verified': bool(verified),
                          'available': bool(connected and verified)})
        return items

    def call(self, slug, agent, tool_id, operation, args):
        slug = self.server.validate_slug(slug)
        self.server.verify_project(slug)
        spec = self.tools.get(tool_id)
        if spec is None or not isinstance(agent, dict) or not agent.get('id'):
            raise ValueError('Okänt verktyg eller okänd anställd')
        if agent.get('station') not in spec.station_ids or operation not in spec.operations:
            raise ValueError('Verktyget är inte tillåtet vid denna arbetsstation')
        # Prevent untrusted prompt text from granting tools. An actual employee
        # must be present in the project and use a supported provider.
        member = next((p for p in self.server.staff_read(slug) if p.get('id') == agent['id']), None)
        if member is None or member.get('provider') not in ('codex', 'gemini') or member.get('work_mode') == 'disabled':
            raise ValueError('Anställd saknar tillstånd att använda verktyg')
        if not all(spec.availability(self.server)):
            raise ValueError('Verktyget saknar verifierad anslutning')
        if not isinstance(args, dict): raise ValueError('Verktygsargument måste vara ett objekt')
        return spec.execute(self.server, slug, operation, args)


def _freesound_available(server):
    import pw_freesound as f
    connected = bool(f.get_key(server))
    return connected, (f.verified_key(server) if connected else False)


def _freesound_execute(server, slug, operation, args):
    import pw_freesound as f
    if operation != 'audio.search': raise ValueError('Okänt Freesound-kommando')
    query = args.get('query')
    if not isinstance(query, str) or not 3 <= len(query.strip()) <= 100 or '\n' in query:
        raise ValueError('Sökningen måste innehålla 3–100 tecken')
    # Server-owned token; no tool response may include it.
    return f.search_freesound(f.get_key(server), query.strip())


def install(server):
    if getattr(server, '_PW_TOOL_REGISTRY', None): return server._PW_TOOL_REGISTRY
    registry = Registry(server)
    registry.register(Tool('freesound', 'Freesound', ('music', 'voice'), ('audio.search',),
                           _freesound_available, _freesound_execute))
    server._PW_TOOL_REGISTRY = registry
    if not hasattr(server, "Handler"):
        return registry  # Lightweight test harness; no HTTP to install.
    previous_get = server.Handler.do_GET

    def do_GET(self):
        url = urlparse(self.path)
        if url.path != '/api/pw-tools/registry': return previous_get(self)
        if not self.allowed() or not self.auth():
            return self.reply(403, {'error':'Ogiltig session'})
        try:
            qs = parse_qs(url.query)
            slug = qs.get('project', [None])[0]
            if slug is not None: server.verify_project(server.validate_slug(slug))
            return self.reply(200, {'tools': registry.list(slug),
                                    'note': 'Installerat är inte samma sak som verifierad anslutning. Återstående kvot är okänd.'})
        except (OSError, ValueError, TypeError) as ex:
            return self.reply(400, {'error': str(ex)[:240]})
    server.Handler.do_GET = do_GET
    return registry
