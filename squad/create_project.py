#!/usr/bin/env python
"""
Create squad project on given instance if the project doesn't exist already.
"""

import argparse
import json
import logging
import os
import sys
import requests


def parse_args():
    """
    Parse script arguments.
    """
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
    parser.add_argument("-s", "--subscriber-email", dest="subscriber_email", default="ci_notify@linaro.org",
                        help="Specify the email address to which the qa_reports email should be sent.")
    parser.add_argument("-l", "--logging", dest="logging", default="INFO",
                        choices=["DEBUG", "INFO"])

    return parser.parse_args()


def get_list(item, args, token):
    """
    Get the list of give items. e.g. projects, groups.
    """
    url = "{}/api/{}/".format(args.url, item)
    headers = {"Authorization": token}

    request = requests.get(url, headers=headers)
    logging.info("%s get request status code: %s", item, request.status_code)
    if request.status_code != 200:
        logging.error("Error fetching %s", url)
        print(request.text)
        sys.exit(1)
    data = request.json()
    items = data["results"]
    while data["next"] is not None:
        url = data["next"]
        data = requests.get(url, headers=headers).json()
        items.extend(data['results'])

    return items

def subscribe_project(data, args, token):
    """
    subscribe to the created project.
    """
    url = "{}/api/projects/".format(args.url)
    headers = {"Authorization": token, "Content-Type": "application/x-www-form-urlencoded"}

    projects = get_list("projects", args, token)
    #logger.debug("Existing project list:\n%s", json.dumps(projects, indent=4))
    for p in projects:
        new_project_full_name = "{}/{}".format(args.group, args.project)
        if new_project_full_name == p["full_name"]:
            project_id=p["id"]
    subscriber_url = "https://staging-qa-reports.linaro.org/api/projects/{}/subscribe/".format(project_id)
    subscriber_data = "email={}".format(args.subscriber_email)
    request = requests.post(subscriber_url, headers=headers, data=subscriber_data)

    if request.status_code != 201:
        logging.error("Error posting %s", subscriber_url)
        # Report the failure
        print(request.text)


def creat_project(data, args, token):
    """
    Create project.
    """
    url = "{}/api/projects/".format(args.url)
    headers = {"Authorization": token}

    request = requests.post(url, headers=headers, data=data)
    logging.info("Projects post request status code: %s", request.status_code)
    if request.status_code != 201:
        logging.error("Error posting %s", url)
        # FIXME: As squad doesn't return new created privated projects, exit normally if
        # the returned msg matches: The fields group, slug must make a unique set.
        print(request.text)
        if "The fields group, slug must make a unique set." in request.json().get("non_field_errors"):
            logging.warning("Project already exist!")
            return
        sys.exit(1)
    logging.info("Project created:\n%s", json.dumps(request.json(), indent=4))


def main():
    """
    Check if specified groups and project exist. Create the given project when it doesn't
    exist already.
    """
    args = parse_args()
    logging.basicConfig(format="%(asctime)s: %(funcName)s: %(levelname)s: %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if args.logging == "DEBUG":
        logger.setLevel(logging.DEBUG)

    auth_token = os.environ.get("SQUAD_AUTH_TOKEN")
    if auth_token is None:
        logger.error("SQUAD_AUTH_TOKEN not provided in environment")
        logger.info("1) Find you token here %s/_/settings/api-token/", args.url)
        logger.info("2) export SQUAD_AUTH_TOKEN='Your token'")
        sys.exit(1)
    token = "Token {}".format(auth_token)

    netrc_path = os.path.expanduser('~/.netrc')
    if os.path.exists(netrc_path):
        logger.warning("""
            ~/.netrc exists, authorization headers set with headers= will be overridden
            if credentials are specified in .netrc. Please rename the file when needed.
            """)

    # Check if specified group exist.
    groups = get_list("groups", args, token)
    logger.debug("Existing group list:\n%s", json.dumps(groups, indent=4))
    groups_slug = [g["slug"] for g in groups]
    if args.group in groups_slug:
        # Get group uri by group slug.
        groups_url = {}
        for group in groups:
            groups_url[group["slug"]] = group["url"]
        group_url = groups_url[args.group]
    else:
        logger.error("Group %s not found!", args.group)
        logger.info("Existing groups:\n%s", groups_slug)
        sys.exit(1)

    # Check if specified project exist.
    projects = get_list("projects", args, token)
    logger.debug("Existing project list:\n%s", json.dumps(projects, indent=4))
    # projects_slug = [p["slug"] for p in projects]
    # print(projects_slug)
    projects_full_name = [p["full_name"] for p in projects]
    new_project_full_name = "{}/{}".format(args.group, args.project)
    if new_project_full_name in projects_full_name:
        logger.warning("Project %s already exists, exiting...", args.project)
        logger.info("Existing project slug list:\n%s", projects_full_name)
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
    logger.info("Data to POST: \n%s", json.dumps(data, indent=4))
    creat_project(data, args, token)
    subscribe_project(data, args, token)


if __name__ == "__main__":
    main()
