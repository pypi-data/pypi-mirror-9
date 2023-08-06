# encoding: utf-8
from time import sleep

from datumutil import values


def datum_scan_iter(table_client, scan):
    terminated = False
    retry = 0
    while not terminated:
        if retry >= 1:
            # throttling the request
            sleep(0.5 * (1 << (retry - 1)))
        result = table_client.scan(scan)
        terminated = result.nextStartKey is None
        records = result.records
        scan.startKey = result.nextStartKey
        if not terminated and len(records) < scan.limit:
            retry += 1
        else:
            retry = 0

        for record in records:
            yield record


def scan_iter(table_client, scan):
    for record in datum_scan_iter(table_client, scan):
        yield values(record)
