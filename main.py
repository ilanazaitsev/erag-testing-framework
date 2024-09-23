import logging
import os
from test_runner.cycle_runner import run_test_cycle
from config import ZEPHYR_API_URL, ZEPHYR_API_TOKEN


def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Logging is set up.")


def validate_env():
    if not ZEPHYR_API_URL or not ZEPHYR_API_TOKEN:
        raise EnvironmentError("Ensure ZEPHYR_API_URL and ZEPHYR_API_TOKEN are set in the environment variables")


def main():
    setup_logging()
    validate_env()

    # Fetch cycle_id from environment variable
    cycle_id = os.getenv("TEST_CYCLE_NUMBER")
    if not cycle_id:
        raise ValueError("TEST_CYCLE_NUMBER environment variable not set")

    logging.info(f"Starting execution of test cycle with ID: {cycle_id}")

    try:
        run_test_cycle(cycle_id)
        logging.info(f"Test cycle {cycle_id} execution completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during test cycle execution: {str(e)}")


if __name__ == "__main__":
    main()
