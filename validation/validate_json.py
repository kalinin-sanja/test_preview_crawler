import traceback
from functools import wraps
from logging import getLogger
from typing import Type, Optional, Union, Callable, Tuple, Sequence

import marshmallow
from flask import request, jsonify
from marshmallow import Schema
from werkzeug import Response, exceptions

from utils import create_response
from validation.constants import ServiceHTTPCodes

logger = getLogger(__name__)

DEFAULT_VALIDATE_METHOD = 'GET'


def validate_json(request_schema: Optional[Type[Schema]] = None,
                  response_schema: Optional[Type[Schema]] = None,
                  methods: Union[str, Sequence[str]] = DEFAULT_VALIDATE_METHOD) -> Callable:
    if isinstance(methods, str):
        methods = {methods}

    methods = set(m.upper().strip() for m in methods)

    def decorator(func) -> Callable:

        @wraps(func)
        def wrapper(*args, **kw) -> Union[str, Tuple[Response, int]]:

            log_prefix = f'[ VALIDATION | {request.remote_addr} {request.method} > {request.url_rule} ]'
            step = 'pre processing'

            try:
                # skip decorator if unexpected HTTP method of request
                if request.method not in methods:
                    logger.debug(f'{log_prefix} skip {request.method} method, validator expect {methods}')
                    return func(*args, **kw)

                # validate request data
                step = 'validate request data'
                if request_schema:
                    validation_schema = request_schema()

                    if not request.is_json:
                        logger.warning(f'{log_prefix} < invalid content-type header')
                        return create_response(status=ServiceHTTPCodes.BAD_REQUEST.value,
                                               message='Invalid content-type header')

                    validation_schema.load(request.json)
                    logger.debug(f'{log_prefix} request body validated')

                # call HTTP handler
                step = 'call HTTP handler'
                status = 200
                result = func(*args, **kw)
                if isinstance(result, tuple):
                    response, status = result
                else:
                    response = result

                if not isinstance(response, Response):
                    response = jsonify(result)

                # validate response data
                step = 'validate response data'
                if response_schema:
                    validation_schema = response_schema()

                    if response.status_code != ServiceHTTPCodes.OK.value:
                        return response, status

                    validation_schema.load(response.json)
                    logger.debug(f'{log_prefix} response validated')

                    # return original json cause validation_schema.dump adds unnecessary fields
                    response = response.json

            except exceptions.BadRequest as err:
                logger.warning(f'{log_prefix} < Step: {step}. Exception: {err}')
                response, status = create_response(status=ServiceHTTPCodes.BAD_REQUEST.value,
                                                   message='invalid requests body')
            except marshmallow.ValidationError as err:
                logger.warning(f'{log_prefix} < Step: {step}. Exception: {err}')
                response, status = create_response(status=ServiceHTTPCodes.UNPROCESSABLE_ENTITY.value,
                                                   message='Validation error:\n' + str(err.messages))
            except NotImplementedError as err:
                logger.warning(f'{log_prefix} < Step: {step}. Exception: {err}')
                response, status = create_response(status=ServiceHTTPCodes.NOT_IMPLEMENTED.value,
                                                   message=type(err).__name__ + '\n' + str(traceback.format_exc()))
            except (TypeError, Exception) as err:  # pylint: disable=broad-except
                logger.warning(f'{log_prefix} < Step: {step}. Exception: {err}')
                response, status = create_response(status=ServiceHTTPCodes.SERVER_ERROR.value,
                                                   message=type(err).__name__ + '\n' + str(traceback.format_exc()))

            return response, status

        return wrapper

    return decorator
