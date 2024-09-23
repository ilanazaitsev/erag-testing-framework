class ZephyrAPIError(Exception):
    """Exception raised for errors in Zephyr API calls."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
