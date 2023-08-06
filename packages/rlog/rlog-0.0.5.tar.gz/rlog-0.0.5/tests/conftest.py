# coding: utf-8
import logging
import pytest

from rlog import RedisHandler


@pytest.fixture
def redis_logger():
    logger = logging.getLogger()
    logger.addHandler(RedisHandler(channel='test'))
    return logger
