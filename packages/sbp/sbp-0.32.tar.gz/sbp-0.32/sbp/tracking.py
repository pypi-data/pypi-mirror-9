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
Satellite code and carrier-phase tracking messages from the Piksi.

"""

from construct import *
import json
from sbp import SBP
from sbp.utils import fmt_repr, exclude_fields, walk_json_dict
import six

# Automatically generated from piksi/yaml/swiftnav/sbp/tracking.yaml
# with generate.py at 2015-04-14 12:12:07.028186. Please do not hand edit!


class TrackingChannelState(object):
  """TrackingChannelState.
  
  Tracking channel state for a specific satellite PRN and measured
signal power.

  
  Parameters
  ----------
  state : int
    Status of tracking channel
  prn : int
    PRN being tracked
  cn0 : float
    Carrier-to-noise density

  """
  _parser = Embedded(Struct("TrackingChannelState",
                     ULInt8('state'),
                     ULInt8('prn'),
                     LFloat32('cn0'),))

  def __init__(self, payload):
    self.from_binary(payload)

  def __repr__(self):
    return fmt_repr(self)
  
  def from_binary(self, d):
    p = TrackingChannelState._parser.parse(d)
    self.__dict__.update(dict(p.viewitems()))

  def to_binary(self):
    return TrackingChannelState.build(self.__dict__)
    
SBP_MSG_TRACKING_STATE = 0x0016
class MsgTrackingState(SBP):
  """SBP class for message MSG_TRACKING_STATE (0x0016).

  You can have MSG_TRACKING_STATE inherent its fields directly
  from an inherited SBP object, or construct it inline using a dict
  of its fields.

  
  The tracking message returns a variable-length array of tracking
channel states. It reports status and code/carrier phase signal
power measurements for all tracked satellites.


  Parameters
  ----------
  sbp : SBP
    SBP parent object to inherit from.
  states : array
    Satellite tracking channel state

  """
  _parser = Struct("MsgTrackingState",
                   OptionalGreedyRange(Struct('states', TrackingChannelState._parser)),)

  def __init__(self, sbp=None, **kwargs):
    if sbp:
      self.__dict__.update(sbp.__dict__)
      self.from_binary(sbp.payload)
    else:
      self.states = kwargs.pop('states')

  def __repr__(self):
    return fmt_repr(self)
 
  def from_binary(self, d):
    """Given a binary payload d, update the appropriate payload fields of
    the message.

    """
    p = MsgTrackingState._parser.parse(d)
    self.__dict__.update(dict(p.viewitems()))

  def to_binary(self):
    """Produce a framed/packed SBP message.

    """
    c = Container(**exclude_fields(self))
    self.payload = MsgTrackingState._parser.build(c)
    return self.pack()

  def to_json(self):
    """Produce a JSON-encoded SBP message.

    """
    d = super( MsgTrackingState, self).to_json_dict()
    j = walk_json_dict(exclude_fields(self))
    d.update(j)
    return json.dumps(d)

  @staticmethod
  def from_json(data):
    """Given a JSON-encoded message, build an object.

    """
    d = json.loads(data)
    sbp = SBP.from_json_dict(d)
    return MsgTrackingState(sbp)
    
SBP_MSG_EPHEMERIS = 0x001A
class MsgEphemeris(SBP):
  """SBP class for message MSG_EPHEMERIS (0x001A).

  You can have MSG_EPHEMERIS inherent its fields directly
  from an inherited SBP object, or construct it inline using a dict
  of its fields.

  
  The ephemeris message returns a set of satellite orbit
parameters that is used to calculate GPS satellite position,
velocity, and clock offset (WGS84). Please see the Navstar GPS
Space Segment/Navigation user interfaces (ICD-GPS-200, Table
20-III) for more details.


  Parameters
  ----------
  sbp : SBP
    SBP parent object to inherit from.
  tgd : double
    Group delay differential between L1 and L2 (?)
  crs : double
    Amplitude of the sine harmonic correction term to the orbit radius
  crc : double
    Amplitude of the cosine harmonic correction term to the orbit radius
  cuc : double
    Amplitude of the cosine harmonic correction term to the argument of latitude
  cus : double
    Amplitude of the sine harmonic correction term to the argument of latitude
  cic : double
    Amplitude of the cosine harmonic correction term to the angle of inclination
  cis : double
    Amplitude of the sine harmonic correction term to the angle of inclination
  dn : double
    Mean motion difference
  m0 : double
    Mean anomaly at reference time
  ecc : double
    Eccentricity of satellite orbit
  sqrta : double
    Square root of the semi-major axis of orbit
  omega0 : double
    Longitude of ascending node of orbit plane at weekly epoch
  omegadot : double
    Rate of right ascension
  w : double
    Argument of perigee
  inc : double
    Inclination
  inc_dot : double
    Inclination first derivative
  af0 : double
    Polynomial clock correction coefficient (clock bias)
  af1 : double
    Polynomial clock correction coefficient (clock drift)
  af2 : double
    Polynomial clock correction coefficient (rate of clock drift)
  toe_tow : double
    Time of week
  toe_wn : int
    Week number
  toc_tow : double
    Clock reference time of week
  toc_wn : int
    Clock reference week number
  valid : int
    Is valid?
  healthy : int
    Satellite is healthy?
  prn : int
    PRN being tracked

  """
  _parser = Struct("MsgEphemeris",
                   LFloat64('tgd'),
                   LFloat64('crs'),
                   LFloat64('crc'),
                   LFloat64('cuc'),
                   LFloat64('cus'),
                   LFloat64('cic'),
                   LFloat64('cis'),
                   LFloat64('dn'),
                   LFloat64('m0'),
                   LFloat64('ecc'),
                   LFloat64('sqrta'),
                   LFloat64('omega0'),
                   LFloat64('omegadot'),
                   LFloat64('w'),
                   LFloat64('inc'),
                   LFloat64('inc_dot'),
                   LFloat64('af0'),
                   LFloat64('af1'),
                   LFloat64('af2'),
                   LFloat64('toe_tow'),
                   ULInt16('toe_wn'),
                   LFloat64('toc_tow'),
                   ULInt16('toc_wn'),
                   ULInt8('valid'),
                   ULInt8('healthy'),
                   ULInt8('prn'),)

  def __init__(self, sbp=None, **kwargs):
    if sbp:
      self.__dict__.update(sbp.__dict__)
      self.from_binary(sbp.payload)
    else:
      self.tgd = kwargs.pop('tgd')
      self.crs = kwargs.pop('crs')
      self.crc = kwargs.pop('crc')
      self.cuc = kwargs.pop('cuc')
      self.cus = kwargs.pop('cus')
      self.cic = kwargs.pop('cic')
      self.cis = kwargs.pop('cis')
      self.dn = kwargs.pop('dn')
      self.m0 = kwargs.pop('m0')
      self.ecc = kwargs.pop('ecc')
      self.sqrta = kwargs.pop('sqrta')
      self.omega0 = kwargs.pop('omega0')
      self.omegadot = kwargs.pop('omegadot')
      self.w = kwargs.pop('w')
      self.inc = kwargs.pop('inc')
      self.inc_dot = kwargs.pop('inc_dot')
      self.af0 = kwargs.pop('af0')
      self.af1 = kwargs.pop('af1')
      self.af2 = kwargs.pop('af2')
      self.toe_tow = kwargs.pop('toe_tow')
      self.toe_wn = kwargs.pop('toe_wn')
      self.toc_tow = kwargs.pop('toc_tow')
      self.toc_wn = kwargs.pop('toc_wn')
      self.valid = kwargs.pop('valid')
      self.healthy = kwargs.pop('healthy')
      self.prn = kwargs.pop('prn')

  def __repr__(self):
    return fmt_repr(self)
 
  def from_binary(self, d):
    """Given a binary payload d, update the appropriate payload fields of
    the message.

    """
    p = MsgEphemeris._parser.parse(d)
    self.__dict__.update(dict(p.viewitems()))

  def to_binary(self):
    """Produce a framed/packed SBP message.

    """
    c = Container(**exclude_fields(self))
    self.payload = MsgEphemeris._parser.build(c)
    return self.pack()

  def to_json(self):
    """Produce a JSON-encoded SBP message.

    """
    d = super( MsgEphemeris, self).to_json_dict()
    j = walk_json_dict(exclude_fields(self))
    d.update(j)
    return json.dumps(d)

  @staticmethod
  def from_json(data):
    """Given a JSON-encoded message, build an object.

    """
    d = json.loads(data)
    sbp = SBP.from_json_dict(d)
    return MsgEphemeris(sbp)
    

msg_classes = {
  0x0016: MsgTrackingState,
  0x001A: MsgEphemeris,
}