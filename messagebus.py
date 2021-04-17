#!/usr/bin/env python3

from typing import NamedTuple
from pymessagebus import MessageBus

class ButtonMessage(NamedTuple):
    PRESSED = 1
    RELEASED = 2

    action: int

class DisplayMessage(NamedTuple):
    message: str
