"""
Collects stack samples (see stacksampler.py) from processes that have reported
a port where it publishes the stacksampler results.
"""
import logging
import subprocess
from io import StringIO

import collections
import gevent
import signal
import requests
from gevent.wsgi import WSGIServer

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from flask import Flask, request, json, Response

STARTING_PORT = 10000
POLL_PERIOD = 10

procs = []
samples = collections.deque(maxlen=1000)


def create_app():
    app = Flask(__name__)
    return app


def configure_routes(app):

    @app.route('/init', methods=['POST'])
    def init():
        if not procs:
            procs.append(STARTING_PORT)
        else:
            procs.append(procs[-1] + 1)
        log.info('Registered process to poll on port: %s', procs[-1])
        return str(procs[-1])

    @app.route('/info')
    def info():
        return json.dumps({
            'polling_ports': procs
        })

    @app.route('/samples')
    def serve_samples():
        return json.dumps({
            'samples': list(samples)
        })

    @app.route('/flamegraph')
    def generate_flamegraph():
        p = subprocess.Popen(['perl', './tools/perf/flamegraph.pl'],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        stdout = p.communicate(merge_samples(samples).encode('utf8'))
        return Response(stdout[0], mimetype='image/svg+xml')


def merge_samples(samples):
    stack_counts = collections.defaultdict(int)
    for sample in samples:
        for line in sample.splitlines()[2:]:
            frame, count = line.split(' ')
            stack_counts[frame] += int(count)
    return '\n'.join([
        '{} {}'.format(frame, count)
        for frame, count
        in stack_counts.items()
    ])


def run_server(app):
    http_server = WSGIServer(('0.0.0.0', 9000), app)
    http_server.serve_forever()


def poll(procs):
    print('Starting poller')
    log.info('Starting stack sample poller')
    gevent.sleep(1)
    while True:
        log.info('Polling %s processes', len(procs))
        for proc in procs:
            resp = requests.get('http://localhost:{}'.format(proc))
            assert resp.status_code == 200, 'Could not collect stack sample'
            log.info('Received stack sample of length %s from %s',
                     len(resp.text), proc)
            samples.append(resp.text)
        gevent.sleep(10)


def shutdown():
    log.info('Shutting down')
    exit(0)


if __name__ == '__main__':
    gevent.signal(signal.SIGQUIT, gevent.kill)
    gevent.signal(signal.SIGTERM, shutdown)

    app = create_app()
    configure_routes(app)

    gevent.joinall([
        gevent.spawn(run_server, app),
        gevent.spawn(poll, procs)
    ])