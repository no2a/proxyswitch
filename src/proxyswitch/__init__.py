import logging
import os
import re
from typing import Optional

from proxy.common.flag import flags
from proxy.http.parser import HttpParser
from proxy.http.url import Url
from proxy.plugin import ProxyPoolPlugin


flags.add_argument(
    '--proxyswitch-config',
    type=str,
    required=True,
    help='Path to proxyswitch config file',
)


LOG = logging.getLogger(__name__)


def _iter_config(f):
    conf = []
    for n, line in enumerate(f):
        if line.startswith('#'):
            continue
        line = line.rstrip()
        if not line:
            continue
        parts = line.split(sep=None, maxsplit=2)
        if len(parts) != 2:
            LOG.warning('ignored invalid config `%s` (line %d)', line, n + 1)
            continue
        yield parts[0], parts[1]


def _find_proxy_url(config_path: str, host: str) -> str:
    proxy_url = 'DIRECT'
    try:
        config_path = os.path.expanduser(config_path)
        with open(config_path) as f:
            for pattern, if_match in _iter_config(f):
                if pattern.startswith('/'):
                    if re.match(pattern[1:], host, re.IGNORECASE):
                        proxy_url = if_match
                        break
                else:
                    if pattern.lower() == host.lower():
                        proxy_url = if_match
                        break
    except Exception:
        LOG.exception('error occured during reading config')
    if proxy_url == 'DIRECT':
        proxy_url = ''
    return proxy_url


class Plugin(ProxyPoolPlugin):

    # 落ちないようにオーバーライド
    def _select_proxy(self):
        return None

    def _set_endpoint_for_request(self, request: HttpParser) -> None:
        host = request.host.decode()
        proxy_url = _find_proxy_url(self.flags.proxyswitch_config, host)
        LOG.debug('use proxy %s for %s', proxy_url, host)
        if proxy_url:
            self._endpoint = Url.from_bytes(proxy_url.encode())
        else:
            self._endpoint = None

    def before_upstream_connection(
            self, request: HttpParser,
    ) -> Optional[HttpParser]:
        self._set_endpoint_for_request(request)
        if self._endpoint:
            return super().before_upstream_connection(request)
        else:
            return request


def main():
    from proxy import entry_point
    entry_point()
