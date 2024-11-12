import json
import logging

from zephyr_client.api import update_test_result_batch, update_test_result

BATCH_SIZE = 10  # Number of test results to batch


def handle_test_result(test_case_id, result):
    print(f"Updating test case {test_case_id} with result: {result}")
    update_test_result(test_case_id, result)


def generate_test_report(cycle_id, failed_tests):
    report = {
        'cycle_id': cycle_id,
        'failed_tests': failed_tests,
        'status': 'Completed' if not failed_tests else 'Completed with Failures'
    }
    with open(f'report_{cycle_id}.json', 'w') as report_file:
        json.dump(report, report_file, indent=4)
    logging.info(f"Test report generated for cycle {cycle_id}.")


def handle_batch_results(test_case_results):
    """
    Handle batch updates for test results.
    """
    batched_results = []

    for test_case_id, result in test_case_results.items():
        batched_results.append({'test_case_id': test_case_id, 'result': result})

        # Once we hit the batch size, send a batch update
        if len(batched_results) >= BATCH_SIZE:
            update_test_result_batch(batched_results)
            batched_results.clear()

    # If any remaining results are left after batching, update them
    if batched_results:
        update_test_result_batch(batched_results)
