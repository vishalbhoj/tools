#!/usr/bin/env python3

import argparse
import requests
import json
import logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='suite__project__slug')
    parser.add_argument('-b', dest='test_run__build__version')
    parser.add_argument('-e', dest='test_run__environment__slug')
    parser.add_argument('-s', dest='suite__slug', nargs='+',
                        help='supports to specify multiple tests separated with space')
    parser.add_argument('-r', dest='result', choices=['True', 'False'])
    args = parser.parse_args()
    return args


def requests_get(endpoint, payload=None):
    if payload is not None:
        r = requests.get(endpoint, params=payload)
    else:
        r = requests.get(endpoint)
    print('\n')
    logging.info('URI: {}'.format(r.url))
    logging.info('status_code: {}'.format(r.status_code))
    logging.debug('returned results: {}'.format(r.json()))
    data = r.json()

    return data


def get_result(endpoint, payload):
    result = []
    data = requests_get(endpoint, payload)
    result.extend(data['results'])

    while data['next'] is not None:
        uri = data['next']
        data = requests_get(uri)
        result.extend(data['results'])

    return result


def collect_results(args):
    endpoint = 'https://qa-reports.linaro.org/api/tests/'
    payload = vars(args)
    logging.info(payload)
    suites = payload['suite__slug']

    # Issue: https://github.com/Linaro/squad/issues/416
    # Workaround: iterate over suites list.
    results = []
    if suites is None:
        results = get_result(endpoint, payload)
    else:
        if not isinstance(suites, list):
            suites = suites.split()
        for suite in suites:
            payload['suite__slug'] = suite
            result = get_result(endpoint, payload)
            results.extend(result)

    return results


def save_results_to_json(results, filename):
    with open('{}.json'.format(filename), 'w') as f:
        json.dump(results, f, indent=4)

    logging.info('detailed results saved to {}.json'.format(filename))


def generate_test_list(results):
    test_list = []
    for result in results:
        if result['short_name'] not in test_list:
            test_case_id = result['short_name']
            # shorten 'VtsKernelLtp.syscalls.open10_64bit' to 'open10'
            # 'VtsKernelLtp.mm.mmapstress07_64bit' to ''
            if 'VtsKernelLtp' in test_case_id:
                try:
                    test_case_id = test_case_id.split('.')[2].split('_')[0]
                except IndexError:
                    # ignore test result like 'VtsKernelLtp.setup_class'
                    pass
            test_list.append(test_case_id)

    return test_list


def save_test_list_to_txt(test_list, filename):
    with open('{}.txt'.format(filename), 'w') as f:
        for test in test_list:
            f.write(test + '\n')

    logging.info('test list saved to {}.txt'.format(filename))


def main():
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s: %(funcName)s: %(message)s"
    )
    logging.debug('args: {}'.format(args))

    results = collect_results(args)

    filename_dict = vars(args)
    for k in filename_dict:
        if filename_dict[k] is None:
            filename_dict[k] = 'all'
    filename = 'project_{}-build_{}-env_{}-result_{}'.format(
        filename_dict['suite__project__slug'],
        filename_dict['test_run__build__version'],
        filename_dict['test_run__environment__slug'],
        filename_dict['result'])

    save_results_to_json(results, filename)
    test_list = generate_test_list(results)
    save_test_list_to_txt(test_list, filename)


if __name__ == '__main__':
    main()
