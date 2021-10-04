from collections import Generator

import requests

from gobexport.config import get_host


class Worker:

    # Header values for Worker Requests and Responses
    _WORKER_REQUEST = "X-Worker-Request"
    _WORKER_ID_RESPONSE = "X-Worker-Id"
    _WORKER_RESULT_OK = "OK"
    _WORKER_RESULT_FAILURE = "FAILURE"

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
        worker_id = response.headers[cls._WORKER_ID_RESPONSE]

        print(f"Worker response {worker_id} started")
        lastline = None
        for line in response.iter_lines():
            lastline = line

        lastline = lastline.decode()
        if lastline == cls._WORKER_RESULT_FAILURE:
            print(f"Worker response {worker_id} failed")
            raise requests.exceptions.RequestException("Worker response failed")
        elif lastline != cls._WORKER_RESULT_OK:
            print(f"Worker response {worker_id} ended prematurely")
            raise requests.exceptions.RequestException("Worker response ended prematurely")
        else:
            print(f"Worker result {worker_id} OK")
            try:
                # Request result
                url = f"{cls._WORKER_API}/{worker_id}"
                response = requests.get(url=url, stream=True)
                response.raise_for_status()

                # yield result
                for line in response.iter_lines():
                    yield line
            except Exception as e:
                print(f"Worker result {worker_id} failed")
                # Re-raise exception
                raise e
            finally:
                # Always try to cleanup worker files (even if an exception has occurred)
                print(f"Worker result {worker_id} clear...")
                url = f"{cls._WORKER_API}/end/{worker_id}"
                response = requests.delete(url=url)
                response.raise_for_status()
