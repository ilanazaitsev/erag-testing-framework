import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import time

from test_runner.result_handler import generate_test_report
from zephyr_client.api import update_test_execution_batch, TestStatus
from test_runner.test_executor import execute_test

MAX_WORKERS = 10  # Consider making this an environment variable
BATCH_SIZE = 10  # Number of updates to batch together when sending status updates
from threading import Lock

# Shared data structure to hold test results
shared_results = {}
results_lock = Lock()  # Lock for thread-safe access to the shared results


def run_single_test(function_name, testcase_function_path, steps_data, test_execution):
    try:
        result = execute_test(function_name, testcase_function_path, steps_data, test_execution)
        logging.info(f"Test {function_name} completed with status: {result}")

        # Update shared results in a thread-safe way
        with results_lock:
            shared_results[function_name] = result

        return function_name, result
    except Exception as e:
        logging.error(f"Error executing test {function_name}: {str(e)}")
        return function_name, "Error"


def execute_tests_in_threads(test_function_map, cycle_id):
    results = {}
    batch_update_data = []  # Hold test execution data for batching

    # Start the monitoring thread
    monitor_thread = threading.Thread(target=monitor_tests, args=(test_function_map,))
    monitor_thread.start()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(run_single_test, function_name, *details): function_name
                   for function_name, details in test_function_map.items()}

        for future in as_completed(futures):
            function_name = futures[future]
            try:
                result = future.result()
                results[function_name] = result
                batch_update_data.append(result)

                # If batch size is reached, send updates
                if len(batch_update_data) >= BATCH_SIZE:
                    update_test_execution_batch(batch_update_data)
                    batch_update_data.clear()

            except Exception as e:
                logging.error(f"Test execution for {function_name} generated an exception: {str(e)}")

        # Send any remaining updates in the batch
        if batch_update_data:
            update_test_execution_batch(batch_update_data)

    # Wait for the monitoring thread to finish
    monitor_thread.join()

    # Generate the report after all tests have run
    test_case_results = {fn: res for fn, res in results.items()}
    generate_test_report(cycle_id, test_case_results)

    return results



def monitor_tests(test_function_map):
    while True:
        time.sleep(5)  # Check every 5 seconds
        with results_lock:
            if len(shared_results) == len(test_function_map):
                logging.info("All tests have been executed.")
                break  # Exit the loop if all tests are done
            else:
                logging.info(f"Tests completed: {len(shared_results)} of {len(test_function_map)}")
