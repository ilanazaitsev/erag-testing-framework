import json
import os
from enum import Enum

import requests
from .auth import get_auth_headers
from .exceptions import ZephyrAPIError

ZEPHYR_API_URL = os.getenv('ZEPHYR_API_URL')
# todo: put here timeouts for each request
class TestStatus(Enum):
    NotExecuted = "Not Executed"
    InProgress = "In Progress"
    Pass = "Pass"
    Fail = "Fail"
    Blocked = "Blocked"
def get_test_cycle(cycle_id):
    url = f"{ZEPHYR_API_URL}/testcycles/{cycle_id}"
    headers = get_auth_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ZephyrAPIError(f"Error fetching cycle: {response.status_code}")
    return response.json()

def get_test_executions_from_cycle(cycle_id):
    url = f"{ZEPHYR_API_URL}/testexecutions"

    params = {
        "projectKey": "ERAG",
        "testCycle":cycle_id
    }
    headers = get_auth_headers()
    response = requests.get(url, headers=headers,params=params)
    if response.status_code != 200:
        raise ZephyrAPIError(f"Error fetching test cases: {response.status_code}")
    return response.json()


def get_test_case_details(test_case_url):
    headers = get_auth_headers()
    response = requests.get(test_case_url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_steps_of_test_case(testExecutionIdOrKey):
    url = f"{ZEPHYR_API_URL}/testexecutions/{testExecutionIdOrKey}/teststeps"
    headers = get_auth_headers()
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('values', [])


def update_test_execution(test_execution,status,actual_end_date,execution_time):
    url = f"{ZEPHYR_API_URL}/testexecutions/{test_execution['id']}"
    headers = get_auth_headers()

    # Create the payload with all optional fields
    payload = {
        "statusName": status,
        "environmentName": "",
        "actualEndDate": actual_end_date,
        "executionTime": execution_time,
        "executedById": "",
        "assignedToId":"",
        "comment":  ""
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload))

    # Raise an exception if the request was not successful
    response.raise_for_status()

    return response.json()
def update_test_status_by_status_id(test_execution,status):
    url = f"{ZEPHYR_API_URL}/statuses/7692940"
    headers = get_auth_headers()
    payload = {
        "id":7692940,
        "project": test_execution['project'],
        "name": status,
        "index": 1,
        "archived": True,
        "default": True
    }
    response = requests.put(url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()


def update_test_result(test_case_id, result):
    url = f"{ZEPHYR_API_URL}/testcases/{test_case_id}/result"
    headers = get_auth_headers()
    payload = {"status": result}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise ZephyrAPIError(f"Error updating result: {response.status_code}")
    return response.json()
def update_test_result_batch():
    pass