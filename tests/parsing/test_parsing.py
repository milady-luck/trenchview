# test rickbot parsing
# test parsing the line
# test linking replies -> pulling user
import logging

from tgtools.parsing import *

logger = logging.getLogger(__name__)

# TODO: generate TgRickbotMessage lists and test parsing + formatting those


def test_1():
    # cool, this works!
    logger.debug(PriceCheck)
    assert True == True
