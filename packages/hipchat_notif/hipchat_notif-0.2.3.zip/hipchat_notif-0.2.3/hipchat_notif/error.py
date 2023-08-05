#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'drogov'

__all__ = ["HipchatError", "HipchatAuthError", "HipchatRoomError", "HipchatMessageError"]


class HipchatError(Exception):
    pass


class HipchatAuthError(HipchatError):
    pass


class HipchatRoomError(HipchatError):
    pass


class HipchatMessageError(HipchatError):
    pass