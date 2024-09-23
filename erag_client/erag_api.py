import requests

def create_data_source_request_body(ds_id=None, ds_type=None, host=None, port=None, user=None, password=None,
                                    database_name=None, schema=None, cloud_ds_extra_param=None):
    return {
  "ds_id":ds_id,
  "type": ds_type,
  "host": host,
  "port": port,
  "user": user,
  "password": password,
  "database_name": database_name,
  "schema": schema,
  "cloud_ds_extra_param":cloud_ds_extra_param
}
def create_data_source(request_body):
    """Example test function to create a data source via eRAG API."""
    log.debug(f"About to execute generate_sql rest call. Request body: {request_body}")
    response = requests.post(f"http://{ERAG_HOST}:{ERAG_PORT}/api/erag-backend/v1/toucan-sql/sql-generation",
                             json=request_body, timeout=1000)
    log.debug(f"generate_sql rest call executed successfully. Response status code: {response.status_code}. "
              f"Response body: {response.text}")
    return response

def delete_data_source(parameters):
    """Example test function to delete a data source via eRAG API."""
    url = f"https://api.erag-system.com/data-source/{parameters['id']}"
    response = requests.delete(url)
    return response.status_code == 200
