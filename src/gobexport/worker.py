import logging
from collections import Generator

import requests

from gobexport.config import get_host

logger = logging.getLogger(__name__)


class Worker:

    # Header values for Worker Requests and Responses
    _WORKER_REQUEST = "X-Worker-Request"
    _WORKER_ID_RESPONSE = "X-Worker-Id"
    _WORKER_RESULT_OK = "OK"
    _WORKER_RESULT_FAILURE = "FAILURE"
    _REQUEST_ID = "X-Request-ID"

    _WORKER_API = f"{get_host()}/gob/public/worker"

    headers = {
        _WORKER_REQUEST: 'true'
    }

    @classmethod
    def handle_response(cls, response: requests.models.Response) -> Generator[str, None, None]:
        """Handle a worker response.

        Read all lines
        Check if last line is OK
        Then get the response file
        And stream its contents
        Finally delete the response file from the server

        :param response: The response from the request made.
        """
        worker_id = response.headers.get(cls._WORKER_ID_RESPONSE)
        current_request_id = response.headers.get(cls._REQUEST_ID)
        logger.info(f"Worker response {worker_id} (request {current_request_id}) started.")
        last_line = None
        for line in response.iter_lines():
            last_line = line

        last_line = last_line.decode()
        if last_line == cls._WORKER_RESULT_FAILURE:
            logger.info(f"Worker response {worker_id} (request {current_request_id}) failed")
            raise requests.exceptions.RequestException("Worker response failed")
        elif last_line != cls._WORKER_RESULT_OK:
            logger.info(f"Worker response {worker_id} (request {current_request_id}) ended prematurely")
            raise requests.exceptions.RequestException("Worker response ended prematurely")
        else:
            logger.info(f"Worker result {worker_id} (request {current_request_id}) OK")
            try:
                # Request worker result
                url = f"{cls._WORKER_API}/{worker_id}"
                response = requests.get(url=url, stream=True)
                response.raise_for_status()

                for line in response.iter_lines():
                    yield line
            except Exception as e:
                logger.error(f"Worker result {worker_id} failed", exc_info=True)
                raise e
            finally:
                # Always try to cleanup worker files (even if an exception has occurred)
                logger.info(f"Worker result {worker_id} (request {current_request_id}) clear...")
                url = f"{cls._WORKER_API}/end/{worker_id}"
                response = requests.delete(url=url)
                response.raise_for_status()
