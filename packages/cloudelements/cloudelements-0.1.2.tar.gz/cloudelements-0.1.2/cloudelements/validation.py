import logging
from validictory import validate
from validictory import ValidationError

log = logging.getLogger(__name__)


class NoDataException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
        log.debug('[event=no_data_exception] Missing data')


def validate_schema(schema):
    def wrapper(func):
        def decorator(*args, **kwargs):
            # For data, we expect it to
            # be in the second or third position
            # in the tuple since the methods follow
            # the format of self, id, data
            data = kwargs.get('data', None)
            if not data:
                l = len(args)
                if l == 1:
                    data = args[0]
                elif l == 2:
                    data = args[1]
                elif l == 3:
                    data = args[2]

            log.debug(
                "[event=validate_schema][schema=%s] Data is: %s",
                schema,
                data
            )

            try:
                validate(data, schema, fail_fast=False)
            except ValidationError as validation_error:
                log.info(
                    "[event=validate_schema][schema=%s] "
                    "Could not validate schema against data=%s",
                    schema, data
                )
                log.info(
                    '[event=validate_schema] Schema valiation message=%s',
                    validation_error.message
                )

                if hasattr(validation_error, 'errors'):
                    return [
                        dict(
                            field=error.fieldname,
                            error=error.value,
                            msg=error.message
                        ) for error in validation_error.errors
                    ]
                return [dict(
                    field=validation_error.fieldname,
                    value=validation_error.value,
                    msg=validation_error.message
                )]

            return func(*args, **kwargs)
        return decorator
    return wrapper
