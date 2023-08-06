#!/usr/bin/env python
# Copyright (C) 2015 Swift Navigation Inc.
# Contact: Fergus Noble <fergus@swiftnav.com>
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.


"""
Satellite acquisition messages from the Piksi.
"""

from construct import *
import json
from sbp import SBP
from sbp.utils import fmt_repr, exclude_fields, walk_json_dict
import six

# Automatically generated from piksi/yaml/swiftnav/sbp/acquisition.yaml
# with generate.py at 2015-04-14 12:12:07.025823. Please do not hand edit!


SBP_MSG_ACQ_RESULT = 0x0015
class MsgAcqResult(SBP):
  """SBP class for message MSG_ACQ_RESULT (0x0015).

  You can have MSG_ACQ_RESULT inherent its fields directly
  from an inherited SBP object, or construct it inline using a dict
  of its fields.

  
  This message describes the results from an attempted GPS signal
acquisition search for a satellite PRN over a code phase/carrier
frequency range. It contains the parameters of the point in the
acquisition search space with the best signal-to-noise (SNR)
ratio.


  Parameters
  ----------
  sbp : SBP
    SBP parent object to inherit from.
  snr : float
    SNR of best point
  cp : float
    Code phase of best point
  cf : float
    Carrier frequency of best point
  prn : int
    PRN identifier of the satellite signal for which
acquisition was attempted


  """
  _parser = Struct("MsgAcqResult",
                   LFloat32('snr'),
                   LFloat32('cp'),
                   LFloat32('cf'),
                   ULInt8('prn'),)

  def __init__(self, sbp=None, **kwargs):
    if sbp:
      self.__dict__.update(sbp.__dict__)
      self.from_binary(sbp.payload)
    else:
      self.snr = kwargs.pop('snr')
      self.cp = kwargs.pop('cp')
      self.cf = kwargs.pop('cf')
      self.prn = kwargs.pop('prn')

  def __repr__(self):
    return fmt_repr(self)
 
  def from_binary(self, d):
    """Given a binary payload d, update the appropriate payload fields of
    the message.

    """
    p = MsgAcqResult._parser.parse(d)
    self.__dict__.update(dict(p.viewitems()))

  def to_binary(self):
    """Produce a framed/packed SBP message.

    """
    c = Container(**exclude_fields(self))
    self.payload = MsgAcqResult._parser.build(c)
    return self.pack()

  def to_json(self):
    """Produce a JSON-encoded SBP message.

    """
    d = super( MsgAcqResult, self).to_json_dict()
    j = walk_json_dict(exclude_fields(self))
    d.update(j)
    return json.dumps(d)

  @staticmethod
  def from_json(data):
    """Given a JSON-encoded message, build an object.

    """
    d = json.loads(data)
    sbp = SBP.from_json_dict(d)
    return MsgAcqResult(sbp)
    

msg_classes = {
  0x0015: MsgAcqResult,
}