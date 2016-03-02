"""
Collects stack samples (see stacksampler.py) from processes that have reported
a port where it publishes the stacksampler results.
"""
import logging
import subprocess

import collections
import threading

import requests
import time

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


def merge_samples(samples, exclude='stacksampler'):
    stack_counts = collections.defaultdict(int)
    for sample in samples:
        if exclude in sample:
            continue
        for line in sample.splitlines()[2:]:
            frame, count = line.split(' ')
            stack_counts[frame] += int(count)
    return '\n'.join([
         '{} {}'.format(frame, count)
         for frame, count
         in stack_counts.items()
     ])


class StackPoller(threading.Thread):

    def __init__(self, procs):
        super(StackPoller, self).__init__()
        self._stop = threading.Event()
        self.procs = procs

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run(self):
        self.poll()

    def poll(self):
        print('Starting poller')
        log.info('Starting stack sample poller')
        time.sleep(2)
        while not self.stopped():
            log.info('Polling %s processes', len(self.procs))
            for proc in self.procs:
                resp = requests.get('http://localhost:{}?reset=true'.format(
                    proc), timeout=0.5)
                assert resp.status_code == 200, 'Could not collect stack sample'
                log.info('Received stack sample of length %s from %s',
                         len(resp.text), proc)
                samples.append(resp.text)
            self.light_sleep(10)

    def light_sleep(self, duration=1):
        for i in range(10):
            if not self.stopped():
                time.sleep(duration)


if __name__ == '__main__':

    app = create_app()
    configure_routes(app)

    poll_thread = StackPoller(procs=procs)
    poll_thread.start()

    try:
        app.run(host='0.0.0.0', port=9000)
    except KeyboardInterrupt:
        poll_thread.stop()
        poll_thread.join()