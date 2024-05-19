import requests
import logging
from ipykernel.kernelbase import Kernel
import pandas as pd
import json
# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from setuptools.command.install import install as _install

LANGDB_QUERY_URL = "http://localhost:8080/query"
class LangDBKernel(Kernel):
    implementation = 'LangDBKernel'
    implementation_version = '1.0'
    language = 'python'
    language_version = '3.8'
    language_info = {
        'name': 'sql',
        'mimetype': 'text/x-sql',
        'file_extension': '.sql',
        'codemirror_mode': 'sql',
    }
    banner = "LangDB - Run LangDB SQL directly in your notebook"

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=True):
        logger.debug("Starting execution of code")
        logger.debug(f"Original code: {code}")

        if code.strip().startswith("RENDER MODEL"):
            # Extract the widget name
            model_name = code.strip().split("RENDER MODEL", 1)[1].strip()
            logger.debug(f"Rendering Model: {model_name}")

            # Construct the URL with the query string
            url = f"https://google.com/your-widget-page?widget={model_name}"
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text
            logger.debug("Render HTML loaded successfully")

            # Display the HTML content
            display_data = {'data': {'text/html': html_content}, 'metadata': {}}
            self.send_response(self.iopub_socket, 'display_data', display_data)
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }

        try:
            response = requests.post(LANGDB_QUERY_URL, json={'query': code})
            response.raise_for_status()
            logger.debug("POST request successful")

            try:
                json_response = response.json()
                logger.debug("JSON response parsed successfully")
            except json.JSONDecodeError:
                logger.warning("JSON parsing failed, returning raw response")
                raw_response = response.text
                if not silent:
                    display_data = {'data': {'text/plain': raw_response}, 'metadata': {}}
                    self.send_response(self.iopub_socket, 'display_data', display_data)
                return {
                    'status': 'ok',
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {},
                }

            # Check for exception in the response
            if json_response.get("exception"):
                raise Exception(json_response["exception"])

            # Convert data to pandas DataFrame
            data = json_response.get("data", [])
            df = pd.DataFrame(data)
            logger.debug(f"DataFrame created with {len(df)} rows")

            # Display the DataFrame if not silent
            if not silent:
                html_output = df.to_html()
                display_data = {'data': {'text/html': html_output}, 'metadata': {}}
                self.send_response(self.iopub_socket, 'display_data', display_data)

            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }

        except requests.exceptions.RequestException as e:
            logger.error("Request failed", exc_info=True)
            return {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': type(e).__name__,
                'evalue': str(e),
                'traceback': [],
            }
        except Exception as e:
            logger.error("An error occurred", exc_info=True)
            return {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': type(e).__name__,
                'evalue': str(e),
                'traceback': [],
            }