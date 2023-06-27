import logging

_LOGGER = None

def get_logger(module: str = None, debug: bool = False) -> logging.Logger:
    """
    Gets and configure the logger from the application
    """
    global _LOGGER
    
    if _LOGGER:
        return _LOGGER

    logger = logging.getLogger(__package__)
    if debug:
        logger.setLevel(logging.DEBUG)

    if not module:
        module = "task"

    formatter = logging.Formatter('[%(levelname)s] jobtools <%(module_arg)s>: %(msg)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _LOGGER = logging.LoggerAdapter(logger, {'module_arg': module})

    return _LOGGER