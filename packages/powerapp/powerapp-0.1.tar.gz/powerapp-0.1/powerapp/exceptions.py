# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger(__name__)


def return_or_raise(result):
    """
    Take the result of sync operation and pass it through if everything is
    okay, or raise AppContainerError, if there is an error
    """
    if 'error' in result:
        err = result['error']
        logger.error(err)
        raise AppContainerError(err)
    return result


class AppContainerError(Exception):
    """
    Base class for all "managed exceptions" we raise
    """
    pass
