import urllib2
import json


def get(url, timeout):
    """Makes a GET request on url.
    The function waits for response till timeout is reached.

    :param str url: Absolute URL to executed the GET request
    :param int timeout: Time till which to wait for response
    :returns: decoded response. If response is JSON, then JSON object is returned.
    """
    f = urllib2.urlopen(url, data=None, timeout=timeout)
    return _parse_resp(f.read())


def post(url, data, timeout):
    """Makes a POST request on url.
    data is sent with the request. data is expected to be a string of JSON object.
    The function waits for response till timeout is reached.

    :param str url: Absolute URL to executed the GET request
    :param str data: stringified JSON data
    :param int timeout: Time till which to wait for response
    :returns: decoded response. If response is JSON, then JSON object is returned.
    """
    data = data.encode('utf-8')
    req = urllib2.Request(url)
    req.add_header('content-type', 'application/json')
    f = urllib2.urlopen(req, data, timeout=timeout)
    return _parse_resp(f.read())


def _parse_resp(resp):
    """Decodes resp. If the decoded resp is JSON, then a JSON object is returned.

    :param bytes resp: Encoded response returned by request.
    :returns: decoded response or parse JSON object if response is JSON.
    """
    parsed = resp.decode('utf-8')
    try:
        return json.loads(parsed)
    except:
        return parsed
