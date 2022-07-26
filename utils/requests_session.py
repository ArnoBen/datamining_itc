from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def get_session(hook_method):
    """
    Args:
        hook_method: hook method that allows tqdm to follow the progression of the requests
    Returns a session with custom parameters
    """
    s = Session()
    s.hooks['response'].append(hook_method)
    retries = Retry(total=5, backoff_factor=0.2, status_forcelist=[500,502,503,504],
                    raise_on_redirect=True, raise_on_status=True)
    adapter = HTTPAdapter(pool_connections=250, pool_maxsize=250, max_retries=retries)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    return s
