import os
import subprocess
import tempfile
import json
from pkg_resources import resource_filename


default_settings = {
    'loadImages': False,
    'resourceTimeout': 60000,
}


phantomjs_js = os.path.abspath(resource_filename(__name__, 'phantomjs.js'))
cmd = ['phantomjs', phantomjs_js]


def request_using_phantomjs(url, method, session=None, **kw):
    phantomjs = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fifo_path = mkfifo(phantomjs)
    settings = dict(default_settings)
    url_without_fragment = url.partition('#')[0]
    request = {
        'timeout': 60000,
        'url': url_without_fragment,
        'wex_url': url,
        'wexout': fifo_path,
        'settings': settings,
    }
    phantomjs.stdin.write(json.dumps(request) + '\n')
    phantomjs.stdin.flush()
    try:
        yield open(fifo_path, 'r')
    finally:
        os.unlink(fifo_path)


def mkfifo(phantomjs):
    basename = 'wex.phantomjs.{}.{}.fifo'.format(os.getpid(), phantomjs.pid)
    fifo_path = os.path.join(tempfile.gettempdir(), basename)
    os.mkfifo(fifo_path)
    return fifo_path
