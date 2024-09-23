import json
import os
import logging

from zephyr_client.api import get_test_cycle, get_test_executions_from_cycle, get_test_case_details, \
    get_steps_of_test_case, update_test_execution, TestStatus
from .result_handler import handle_test_result
from .test_executor import execute_test, get_test_function  # Import get_test_function
from .thread_manager import execute_tests_in_threads

# Configure logging to a file for tracking test cycle status
logging.basicConfig(filename='test_cycle_log.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionary to hold test function mappings
test_function_map = {}


def run_test_cycle(cycle_id):
    cycle = get_test_cycle(cycle_id)
    logging.info(f"Starting test cycle: {cycle['name']}")

    test_executions_data = get_test_executions_from_cycle(cycle_id)

    if not test_executions_data['values']:
        logging.warning(f"No executions found for test cycle {cycle_id}")
        return

    failed_tests = []

    #1: Collect test functions
    for test_execution in test_executions_data['values']:
        test_case_url = test_execution.get('testCase', {}).get('self')
        if test_case_url:
            try:
                # Get test case details
                test_case_details = get_test_case_details(test_case_url)
                testcase_function_name = 'test_' + test_case_details['name']
                testcase_function_path = check_test_exists(testcase_function_name)

                if testcase_function_path is None:
                    logging.error(f"Test implementation for {testcase_function_name} not found.")
                    raise FileNotFoundError(f"No function found for {testcase_function_name}")

                # Get the test function and map it
                test_function = get_test_function(testcase_function_path, testcase_function_name)

                test_params = get_test_case_parmas(test_execution)
                test_function_map[testcase_function_name] = (test_function, test_params, test_execution)

            except Exception as e:
                logging.error(f"Error processing test {test_case_details['name']}: {str(e)}")
                failed_tests.append({
                    'test_case': test_case_details['name'],
                    'error': str(e)
                })

    # 2: Clean and execute tests in threads
    execute_tests_in_threads(test_function_map)

    # Log final results
    if failed_tests:
        logging.error(f"Test Cycle {cycle_id} completed with failures. Summary:")
        for failure in failed_tests:
            logging.error(f"Test Case: {failure['test_case']} | Error: {failure['error']}")
    else:
        logging.info(f"Test Cycle {cycle_id} completed successfully with no failures.")


def check_test_exists(testcase_name):
    tests_directory = os.path.abspath('tests')

    for root, dirs, files in os.walk(tests_directory):
        if f"{testcase_name}.py" in files:
            return os.path.join(root, f"{testcase_name}.py")

    return None


def get_test_case_parmas(test_execution):
    # todo : put here try except for get_steps_of_test_case
    steps = get_steps_of_test_case(test_execution['key'])
    result = {}
    for i, step in enumerate(steps):
        step_info = step.get('inline', {})
        description = step_info.get('description', '')
        test_data = step_info.get('testData', None)
        expected_result = step_info.get('expectedResult', '')

        result[i] = {
            'description': description,
            'testData': test_data,
            'expectedResult': expected_result
        }

    return result




