#!/usr/bin/env python3

import yaml
import requests
import argparse


def get_known_issues(filename):
    url = "https://raw.githubusercontent.com/Linaro/qa-reports-known-issues/master/{0}".format(filename)
    r = requests.get(url)
    print("URI: ", r.url)
    print("status_code: ", r.status_code)
    data = r.text

    # save downloaded data as record.
    with open(filename, "w") as f:
        f.write(data)

    data_dict = yaml.load(data)
    return data_dict


def list_by_project_env(project, env, raw_data):
    issues = raw_data['projects'][0]['known_issues']

    issue_list = []
    for issue in issues:
        if project in issue['projects'] and env in issue['environments']:
            # remove test suite name from test name 'ltp-syscalls-tests/bind02'
            test_name = issue['test_name'].split('/')[1]
            issue_list.append(test_name)

    return issue_list


def save_to_txt(filename, issue_list):
    with open(filename, 'w') as fp:
        for issue in issue_list:
            fp.write('{}\n'.format(issue))

    print('Known issue list saved to: ', filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', dest='filename', default='ltp-production.yaml',
                        help="Specify known issue filename, refer to https://github.com/Linaro/qa-reports-known-issues")
    parser.add_argument('-p', '--project', dest='project', required=True,
                        help='Specify project name. Example: lkft/linux-stable-rc-4.14-oe')
    parser.add_argument('-e', '--env', dest='env', required=True,
                        help='Specify test environment. Example: hi6220-hikey')
    args = parser.parse_args()

    raw_data = get_known_issues(args.filename)
    issue_list = list_by_project_env(args.project, args.env, raw_data)

    filename = '{}-{}-known-issues'.format(args.project.replace('/', '-'), args.env)
    save_to_txt(filename, issue_list)


if __name__ == '__main__':
    main()
