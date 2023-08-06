# -*- coding: utf-8 -*-


from oslo.config import cfg
import logging

def start_logging():
    logger = logging.getLogger('cloudutils')

    loglevel = logging.DEBUG if cfg.CONF.debug else logging.INFO
    logger.setLevel(loglevel)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)

    # create formatter
    formatter = logging.Formatter('%(asctime)s (%(levelname)s) %(message)s',
                                '%H:%M:%S')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


    return logger
