import hashlib

from requests.utils import default_user_agent as requests_user_agent

import hatcher


def compute_sha256(filename, block_size=16384):
    m = hashlib.sha256()
    with open(filename, "rb") as fp:
        while True:
            data = fp.read(block_size)
            if data == b"":
                break
            m.update(data)
    return m.hexdigest()


def hatcher_user_agent():
    return 'hatcher/{0} {1}'.format(
        hatcher.__version__, requests_user_agent())
