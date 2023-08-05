# -*- coding: utf-8 -*-

class GeneralError(Exception):
  def __init__(self, value):
    self._value = value

  def __str__(self):
    return repr(self._value)


class BUFRError(GeneralError):
  def __init__(self, value):
    super().__init__(value)
