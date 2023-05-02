from logging import getLogger
from typing import Dict
from typing import Tuple

from flask import jsonify
from flask.wrappers import Response

from schema.preview_scheme import ErrorScheme

logger = getLogger(__name__)


def create_response(data: dict = None, status: int = 200, message: str = '') -> \
        Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.

    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <dict> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int
    """
    if data is not None:
        if not isinstance(data, Dict):  # pylint: disable=isinstance-second-argument-not-valid-type
            try:
                data = data.__dict__
            except AttributeError as err:
                logger.error('Cannot cast object to dict representation. Raise error.')
                raise TypeError(f'Data should be a dictionary. {err}') from err

    success = 200 <= status < 300

    if success:
        res = data
    else:
        res = ErrorScheme().dump({'error': {'message': message}})

    response = jsonify(res)

    response.status_code = status
    return response, status
