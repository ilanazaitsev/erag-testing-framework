import importlib
import logging
import os
import time
from datetime import datetime
from zephyr_client.api import update_test_status_by_status_id, TestStatus, update_test_execution

RETRY_LIMIT = 3  # Retry limit for Zephyr API calls in case of rate limiting


def get_current_time():
    return datetime.utcnow().isoformat() + 'Z'


def get_test_function(testcase_function_path, function_name):
    tests_directory = os.path.abspath('tests')
    module_path = os.path.relpath(testcase_function_path, start=tests_directory)
    module_name = module_path.replace(os.sep, '.')[:-3]  # Convert to module name, remove .py

    try:
        module = importlib.import_module(f"tests.{module_name}")
        test_function = getattr(module, function_name)
        return test_function
    except AttributeError:
        raise ImportError(f"Test function '{function_name}' not found in module 'tests.{module_name}'")
    except Exception as e:
        raise ImportError(f"Error importing function '{function_name}': {str(e)}")


def retry_on_failure(func, *args, retries=RETRY_LIMIT):
    attempt = 0
    while attempt < retries:
        try:
            return func(*args)  # Try executing the function
        except Exception as e:
            attempt += 1
            logging.warning(f"Retry {attempt} for {func.__name__} due to: {str(e)}")
            time.sleep(1)  # Short delay before retrying
    logging.error(f"Failed after {retries} retries for {func.__name__}.")
    raise Exception(f"{func.__name__} failed after {retries} retries.")


def execute_test(test_function, steps_data, test_execution):
    test_execution_id = test_execution['key']
    start_time = time.time()

    try:
        # Update test to "Not Executed" at the beginning
        retry_on_failure(update_test_execution, test_execution, TestStatus.NotExecuted.value, '', '')

        # Set test status to "In Progress"
        retry_on_failure(update_test_execution, test_execution, TestStatus.InProgress.value, get_current_time(), 0)

        # Execute the actual test function
        result = test_function(steps_data)
        execution_time = int((time.time() - start_time) * 1000)  # in milliseconds

        if result == "Pass":
            status = TestStatus.Pass.value
            logging.info(f"Test {test_execution_id}: Passed")
        else:
            status = TestStatus.Fail.value
            logging.info(f"Test {test_execution_id}: Failed")

    except Exception as func_error:
        status = TestStatus.Fail.value
        logging.error(f"Test {test_execution_id}: Failed during execution - {str(func_error)}")
        raise RuntimeError(f"Test execution failed: {str(func_error)}")

    finally:
        actual_end_date = get_current_time()
        retry_on_failure(update_test_execution, test_execution, status, actual_end_date, execution_time)

    return status
