import argparse
import json
import os
import socket

import logging
from time import sleep

import requests

from cua import Queue, Config

logger = logging.getLogger('newrelic_counter_queue')
newrelic_guid = "com.webgeoservices.counter_queue"

def parse_config_file(config_file):
    config_values = {}
    try:
        config = open(config_file, 'r')
    except IOError:
        logger.error("newrelic sysmond config file is unreachable")
        return False
    else:
        for line in config.readlines():
            if line[0] != "#" and len(line.strip()) != 0:
                config_var = line.split("=")
                config_values[config_var[0].strip()] = config_var[1].strip()
        config.close()
    return config_values


def set_environment_variables(config_values):
    if "NEWRELIC_LICENCE_KEY" not in os.environ:
        os.environ["NEWRELIC_LICENCE_KEY"] = config_values.get("license_key", "")
    if "NEWRELIC_HOSTNAME" not in os.environ:
        if "hostname" in config_values:
            os.environ["NEWRELIC_HOSTNAME"] = config_values["hostname"]
        else:
            hostname = socket.gethostname()
            os.environ["NEWRELIC_HOSTNAME"] = hostname


def setup_arg_parser():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--log', dest='loglevel', default="ERROR",
                        help='Define LogLevel')
    return parser

def setup_logger(loglevel):
    logger.setLevel(loglevel)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

def set_headers():
    headers = {
        'X-License-Key': os.environ.get("NEWRELIC_LICENCE_KEY", None),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    return headers

def set_datas(queue_state):
    process_id = os.getpid()
    lvm_datas = {
          "agent": {
            "host": os.environ["NEWRELIC_HOSTNAME"],
            "pid": process_id,
            "version": "0.0.1"
          },
          "components": [
            {
              "name": os.environ["NEWRELIC_HOSTNAME"],
              "guid": newrelic_guid,
              "duration": 60,
              "metrics": {
                "Component/queue/Todo/[Count]": int(queue_state['todo']),
                "Component/queue/Doing/[Count]": int(queue_state['doing']),
                "Component/queue/Failed/[Count]": int(queue_state['failed'])
              }
            }
          ]
        }
    return lvm_datas


def post_response(headers, datas):
    response = requests.post(
        "https://platform-api.newrelic.com/platform/v1/metrics",
        json.dumps(datas),
        headers=headers
    )

    if response.status_code != 200:
        try:
            json_response = json.loads(response.content)
            logger.error(json_response["error"])
        except:
            logger.critical(response.content)
    else:
        resp = response.json()
        logger.info(json.dumps(datas))
        logger.info("""Send datas to Newrelic : %s"""%resp["status"])


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()
    loglevel = args.loglevel
    setup_logger(getattr(logging, loglevel.upper(), None))
    redis_config = Config(
        host=os.environ.get('REDIS_HOST', ''),
        port=os.environ.get('REDIS_PORT', 6379),
        database=os.environ.get('REDIS_DATABASE', 1),
        prefix=os.environ.get('REDIS_QUEUE_PREFIX', 'counter')
    )
    queue = Queue(redis_config)

    while True:
        try:
            queue_state = {
                'todo': queue.get_todo_count(),
                'doing': queue.get_doing_count(),
                'failed': queue.get_failed_count()
            }
            headers = set_headers()
            datas = set_datas(queue_state)
            post_response(headers=headers, datas=datas)
            sleep(60)
        except KeyboardInterrupt:
            exit()


if __name__ == "__main__":
    exit(main())