#!/usr/bin/env python

import argparse
import json
import os
import requests
import sys
import logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url",
                        default="https://staging-qa-reports.linaro.org",
                        help="squad instance URL.")
    parser.add_argument("-p", "--project", dest="project", required=True,
                        help="Specify project name.")
    parser.add_argument("-g", "--group", dest="group", default="staging-lkft",
                        help="Specify project name.")
    parser.add_argument('-P', "--is-public", dest='is_public', default=True,
                        choices=["True", "False"],
                        help="Public or private project. Defaults to private.")
    parser.add_argument("-e", "--html-email", dest="html_email", default=False,
                        choices=["True", "False"],
                        help="Set to True to enable HTML version email report.")
    parser.add_argument("-l", "--logging", dest="logging", default="INFO",
                        choices=["DEBUG", "INFO"])

    return parser.parse_args()


def get_list(item, args):
    url = "{}/api/{}/".format(args.url, item)
    auth_token = os.environ.get("SQUAD_AUTH_TOKEN")
    headers = {"Authorization": "Token {}".format(auth_token)}

    r = requests.get(url, headers=headers)
    logging.info("{} get request status code: {}".format(item, r.status_code))
    if r.status_code != 200:
        logging.error("Error fetching {}".format(url))
        print(r.text)
        sys.exit(1)
    data = r.json()
    items = data["results"]
    while data["next"] is not None:
        url = data["next"]
        data = requests.get(url, headers).json()
        items.extend(data['results'])

    return items


def creat_project(data, args):
    url = "{}/api/projects/".format(args.url)
    auth_token = os.environ.get("SQUAD_AUTH_TOKEN")
    headers = {"Authorization": "Token {}".format(auth_token)}

    r = requests.post(url, headers=headers, data=data)
    logging.info("Projects post request status code: {}".format(r.status_code))
    # r.raise_for_status()
    logging.info("Project created:\n{}".format(json.dumps(r.json(), indent=4)))


def main():
    args = parse_args()
    logging.basicConfig(format="%(asctime)s: %(funcName)s: %(levelname)s: %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if args.logging == "DEBUG":
        logger.setLevel(logging.DEBUG)

    auth_token = os.environ.get("SQUAD_AUTH_TOKEN")
    if auth_token is None:
        logger.error("SQUAD_AUTH_TOKEN not provided in environment")
        logger.info("1) Find you token here {}/_/settings/api-token/".format(args.url))
        logger.info("2) export SQUAD_AUTH_TOKEN='Your token'")
        sys.exit(1)

    netrc_path = os.path.expanduser('~/.netrc')
    if os.path.exists(netrc_path):
        logger.warning("""
            ~/.netrc exists, authorization headers set with headers= will be overridden
            if credentials are specified in .netrc. Please rename the file when needed.
            """)

    # Check if specified group exist.
    groups = get_list("groups", args)
    logger.debug("Existing group list:\n{}".format(json.dumps(groups, indent=4)))
    groups_slug = [g["slug"] for g in groups]
    if args.group in groups_slug:
        # Get group uri by group slug.
        groups_url = {}
        for g in groups:
            groups_url[g["slug"]] = g["url"]
        group_url = groups_url[args.group]
    else:
        logger.error("Group {} not found!".format(args.group))
        logger.info("Existing groups:\n{}".format(groups_slug))
        sys.exit(1)

    # Check if specified project exist.
    projects = get_list("projects", args)
    logger.debug("Existing project list:\n{}".format(json.dumps(projects, indent=4)))
    # projects_slug = [p["slug"] for p in projects]
    # print(projects_slug)
    projects_full_name = [p["full_name"] for p in projects]
    new_project_full_name = "{}/{}".format(args.group, args.project)
    if new_project_full_name in projects_full_name:
        logger.warning("Project {} already exists, exiting...".format(args.project))
        logger.info("Existing project slug list:\n{}".format(projects_full_name))
        sys.exit(0)

    data = {
        "group": group_url,
        "slug": args.project,
        "name": args.project,
        "is_public": args.is_public,
        "html_mail": args.html_email,
        "moderate_notifications": False,
        "description": "",
        "important_metadata_keys": "build-url\r\ngit branch\r\ngit commit\r\ngit describe\r\ngit repo",
        # FIXME: enabling plugins not working.
        # Tracking with https://github.com/Linaro/squad/issues/493
        "enabled_plugins_list": ["ltp"],
        "wait_before_notification": 600,
        "notification_timeout": 18000,
        "data_retention_days": 0,
        "project_settings": "{}",
        "custom_email_template": "https://staging-qa-reports.linaro.org/api/emailtemplates/1/"
    }
    logger.info("Data to POST: \n{}".format(json.dumps(data, indent=4)))
    creat_project(data, args)


if __name__ == "__main__":
    main()
