from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from tqdm import tqdm


def get_session(collection=None):
    """
    Args:
        collection (collection): collection on which tqdm will loop
    Returns a session with custom parameters
    """
    s = Session()
    retries = Retry(total=5, backoff_factor=0.2, status_forcelist=[500,502,503,504],
                    raise_on_redirect=True, raise_on_status=True)
    adapter = HTTPAdapter(pool_connections=250, pool_maxsize=250, max_retries=retries)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    if collection:
        tracker = RequestTracker(collection)
        s.hooks['response'].append(tracker.request_fulfilled)
    return s


class RequestTracker:
    def __init__(self, collection):
        self.tqdm_track_requests = tqdm(total=len(collection))

    def request_fulfilled(self, r, *args, **kwargs):
        """Allows for tdqm to track the progress"""
        self.tqdm_track_requests.update()
