"""Core."""

import threading
import logging
import sys
import pickle
import struct
import time
import argparse
import socket

from datasift.client import Client


def get_balance_metrics(balance_data, ts=None):
    """
    Return a list of balance metrics.

    Parsed from the [balance](http://dev.datasift.com/docs/api/1/balance)
    endpoint.
    """
    ts = ts or time.time()

    return [
        ('datasift.balance.credit', (ts, balance_data['balance']['credit']))
    ]


def get_usage_metrics(client_data, ts=None):
    """
    Return a list of usage metrics.

    Parsed from the [usage](http://dev.datasift.com/docs/api/1/usage)
    endpoint.
    """
    ts = ts or time.time()
    output = []

    total_streams = len(client_data['streams'].keys())

    output.append(
        ('datasift.usage.total_streams', (ts, total_streams)))

    for name, data in client_data['streams'].items():
        key = 'datasift.usage.streams.{}'.format(name)
        output.append(('{}.seconds'.format(key), (ts, data['seconds'])))

        if not data.get('licenses'):
            continue

        for license_name, license_value in data['licenses'].items():
            license_name = license_name.replace('.', '-')
            license_key = '{}.licenses.{}'.format(key, license_name)
            output.append((license_key, (ts, license_value)))

    return output


def _update_dpu_object(output, client, stream):
    output[stream] = client.dpu(stream)


def get_dpu_data(client, streams):
    """
    Return a list of streams and their DPU credits.

    Creates a new thread for each API call.

    Warning: this may chew through you Rate Limiting credits, if you
    have enough streams.
    """
    output = {}

    thread_list = []
    for stream in streams:
        t = threading.Thread(
            target=_update_dpu_object, args=(output, client, stream))
        t.start()
        thread_list.append(t)

    for thread in thread_list:
        thread.join()

    return output


def get_dpu_metrics(dpu_data, ts=None):
    """
    Return a list of DPU metrics.

    Expects a dict of DPU items returned from ``get_dpu_data``.
    """
    ts = ts or time.time()

    output = []

    for name, data in dpu_data.items():
        output.append((
            'datasift.dpu.streams.{}.dpu'.format(name), (ts, data['dpu'])))
        output.append((
            'datasift.dpu.streams.{}.count'.format(name),
            (ts, data['detail']['in']['count'])))

        for stream_name, stream_data in (
            data['detail']['in']['targets'].items()
        ):
            stream_name = stream_name.replace('.', '-')
            output.append((
                'datasift.dpu.streams.{}.targets.{}.dpu'.format(
                    name, stream_name),
                (ts, stream_data['dpu'])))
            output.append((
                'datasift.dpu.streams.{}.targets.{}.count'.format(
                    name, stream_name),
                (ts, stream_data['count'])))

    return output


def send_to_graphite(metrics, args):
    """
    Send a list of metrics to Graphite.

    Uses the [pickle protocol](
    http://graphite.readthedocs.org/en/1.0/
    feeding-carbon.html#the-pickle-protocol).
    """
    payload = pickle.dumps(metrics)
    header = struct.pack('!L', len(payload))
    sock = socket.socket()
    sock.connect((args.graphite_host, args.graphite_port))
    sock.sendall('{}{}'.format(header, payload))
    return sock.close()


def get_args():
    """Register and retrieve arguments."""
    parser = argparse.ArgumentParser(
        description='Send account-related Datasift metrics to Graphite.')
    parser.add_argument(
        '-u', '--user', help='username for the DataSift platform',
        required=True)
    parser.add_argument(
        '-k', '--apikey', help='API key for the DataSift platform',
        required=True)
    parser.add_argument(
        '-g', '--graphite-host',
        help='Graphite hostname', required=True)
    parser.add_argument(
        '-p', '--graphite-port',
        help='Graphite port', default=2004, type=int)
    parser.add_argument(
        '-s', '--include-dpu-stats',
        help=(
            'Include DPU stats? Warning: with a lot of streams this could '
            'chew through your Rate Limit credits.'),
        default=False, action='store_true')
    parser.add_argument(
        '-e', '--period',
        help="Period for stats retrieval (default 'current').",
        choices=('current', 'day', 'hour'),
        default='current')
    parser.add_argument(
        '-i', '--interval',
        help='Interval in minutes to run stats collector (default 5 mins).',
        default=5, type=int)
    parser.add_argument(
        '-d', '--debug',
        help='Run in debug mode (log stuff to stdout).',
        default=False, action='store_true')
    return parser.parse_args()


def main():
    """Main loop."""
    args = get_args()

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(stream=sys.stdout, level=level)

    while True:
        c = Client(user=args.user, apikey=args.apikey)

        logging.debug('Retrieving balance data.')
        balance_data = c.balance()
        logging.debug(balance_data)

        logging.debug('Parsing balance metrics.')
        balance_metrics = get_balance_metrics(c.balance())
        logging.debug(balance_metrics)

        logging.debug('Sending balance metrics to Graphite.')
        send_to_graphite(balance_metrics, args)

        logging.debug('Retrieving usage data.')
        usage_data = c.usage(args.period)
        logging.debug(usage_data)

        if args.include_dpu_stats:
            streams = usage_data['streams'].keys()
            logging.debug('Preparing DPU data.')
            dpu_data = get_dpu_data(c, streams)
            logging.debug(dpu_data)
            dpu_metrics = get_dpu_metrics(dpu_data)
            logging.debug(dpu_metrics)

            logging.debug('Sending dpu metrics to Graphite.')
            send_to_graphite(dpu_metrics, args)

        logging.debug('Parsing usage metrics.')
        usage_metrics = get_usage_metrics(usage_data)
        logging.debug(usage_metrics)

        logging.debug('Sending usage metrics to Graphite.')
        send_to_graphite(usage_metrics, args)

        logging.debug('Sleeping for {} minutes.'.format(args.interval))
        time.sleep(args.interval * 60)


if __name__ == '__main__':
    main()
