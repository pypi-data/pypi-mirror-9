# -*- coding: utf-8 -*-
import struct
import datetime
import json
import os

from . import Error

_arg_type = {
  'string': 0,
  'vint': 1,
  'int': 2,
  'uint': 3,
  'int8': 4,
  'uint8': 5,
  'int16': 6,
  'uint16': 7,
  'description': 1000,
}

class Reader():
  def __init__(self, filename=None, userA_tbl=None, userB_tbl=None, userC_tbl=None, userD_tbl=None, sec1_func=None, sec2_func=None):
    if isinstance(filename, str):
      self.__f = filename
    else:
      self.__f = None
    self.__fp = None

    self.__sec1func = sec1_func
    self.__sec2func = sec2_func

    self._section0 = {'total_length': -1, 'version': -1}
    self._section1 = {'length': -1, 'master_table': -1}
    self._section2 = {'length': 0}
    self._section3 = {'length': 0, 'subsets': 0, 'is_observation': False, 'is_compress': False, 'description': []}
    self._section4 = {'length': 0, 'data': []}

    self.__read_size = 0

    self.__userB_tbl = userB_tbl
    self.__userD_tbl = userD_tbl

    self.__user_tableB = None
    self.__user_tableD = None

  @property
  def version(self):
    return self._section0['version']

  @property
  def length(self):
    return self._section0['total_length']

  @property
  def data(self):
    return self._section4['data']

  @property
  def date(self):
    return self._section1['time']

  def __del__(self):
    if self.__fp is not None:
      self.close()

  def __enter__(self):
    if self.__f is None:
      raise SyntaxError('File is not assign')
    self.open(self.__f)
    self.read()

    return self

  def __exit__(self, t, v, tb):
    self.close()
    return True

  def __read_octet(self, octet, type=_arg_type['int']):
    if self.__fp is not None:
      b = self.__fp.read(octet)
      self.__read_size += octet
      if type == _arg_type['string']:
        return b.decode('utf-8')
      elif type == _arg_type['vint']:
        v = 0
        for x in range(octet):
          v = v * 256 + b[x]
        return v
      elif type == _arg_type['int8']:
        return struct.unpack('>b', b)[0]
      elif type == _arg_type['uint8']:
        return struct.unpack('>B', b)[0]
      elif type == _arg_type['int16']:
        return struct.unpack('>h', b)[0]
      elif type == _arg_type['uint16']:
        return struct.unpack('>H', b)[0]
      elif type == _arg_type['description']:
        desc = struct.unpack('>bb', b)
        F = (desc[0] & 0b11000000) >> 6
        X = (desc[0] & 0b00111111)
        return F, X, desc[1]
      else:
        return b
    else:
      raise Error.BUFRError('Not reading')

  def __get_bufr_param(self, k):
    w = None
    if self.__user_tableB is not None:
      if k in self.__user_tableB:
        try:
          w = self.__user_tableB[k]['width']
          r = self.__user_tableB[k]['reference']
          s = self.__user_tableB[k]['scale']
          u = self.__user_tableB[k].get('unit', '')
          n = self.__user_tableB[k].get('name', None)
          t = self.__user_tableB[k].get('table', None)
          return w, r, s, u, n, t
        except KeyError:
          raise Error.BUFRError('User table {t} is broken'.format(t=self.__userB_tbl))
    for v in self.__tableB[k]:
      if self._section1['master-table-version'] in v['version']:
        w = v['width']
        r = v['reference']
        s = v['scale']
        u = v['unit']
        n = v['name']
        t = v.get('table', None)
        return w, r, s, u, n, t
    raise Error.BUFRError('BUFR table configure is broken')

  def __read_table(self):
    d = os.environ.get('PYWMOFILES_CONFIG', os.path.dirname(__file__))

    with open(d + '/tables/BUFR_tblB.json', 'r') as f:
      self.__tableB = json.loads(f.read())

    with open(d + '/tables/BUFR_tblD.json', 'r') as f:
      self.__tableD = json.loads(f.read())

    if self.__userB_tbl is not None:
      with open(self.__userB_tbl, 'r') as f:
        self.__user_tableB = json.loads(f.read())

    if self.__userD_tbl is not None:
      with open(self.__userD_tbl, 'r') as f:
        self.__user_tableD = json.loads(f.read())

  def __read_bit(self, buf, start, length):
    total_bit = 8 * len(buf)
    v = 0
    for x in range(total_bit + 1):
      b = x // 8
      if start > x:
        continue
      if start + length - 1 < x:
        v = v // 2
        break
      bp = 8 - (x - (8 * b))
      m = 2 ** (bp - 1)
      if (buf[b] & m)>>(bp - 1) == 1:
        v += 1
      else:
        v += 0
      v *= 2
    return v

  def __read_bit_by_string(self, buf, start, length):
    v = self.__read_bit(buf, start, length)
    s = ''
    while True:
      t = v % 256
      c = struct.pack('B', t).decode('utf-8')
      v = (v - t) // 256
      s += c
      if v == 0:
        break
    return s[::-1]

  def __read_bit_stream(self, length, buf, pos, is_string=False):
    start_bit = pos
    end_bit = pos + length
    start_octet = start_bit // 8
    end_octet = end_bit // 8 + 1
    if end_bit % 8 == 0:
      end_octet -= 1

    #uprint(start_octet, start_octet * 8, end_octet, end_octet * 8, pos, length, len(buf))
    if is_string is False:
      return self.__read_bit(buf[start_octet:end_octet], start_bit - start_octet * 8, length)
    else:
      return self.__read_bit_by_string(buf[start_octet:end_octet], start_bit - start_octet * 8, length)

  def __unpack_value(self, k, data, pos):
    w, r, s, u, n, t = self.__get_bufr_param(k)
    m = 2 ** w - 1

    if not u.startswith('CCITT'):
      bs = self.__read_bit_stream(w, data, pos)
      if bs == m:
        return None, w, u, n, t
      v = (bs + r) / (10 ** s)
      if s == 0:
        v = int(v)
    else:
      v = self.__read_bit_stream(w, data, pos, is_string=True)
      v = v.strip()
    return v, w, u, n, t

  def __read_data(self, data):
    ret = []
    length = (self._section4['length'] - 4) * 8
    bit_pos = 0
    for x in range(self._section3['subsets']):
      proc = self._section3['description'][:]
      da = []
      while (length - bit_pos) > 0 and len(proc) > 0:
        d = proc.pop(0)
        k = '{F:01d}{X:02d}{Y:03d}'.format(**d)

        if d['F'] == 0:
          v, w, u, n, t = self.__unpack_value(k, data, bit_pos)
          bit_pos += w
          da.append({'key':k, 'name': n, 'unit': u, 'table': t, 'value': v})
        elif d['F'] == 1:
          rc = d['X']
          cnt = d['Y']
          if cnt == 0:
            d = proc.pop(0)
            k = '{F:01d}{X:02d}{Y:03d}'.format(**d)
            v, w, u, n, t = self.__unpack_value(k, data, bit_pos)
            bit_pos += w
            cnt = v
          tmp = []
          for x in range(rc):
            d = proc.pop(0)
            tmp.append(d)
          tmp = tmp * cnt
          tmp.extend(proc)
          proc = tmp[:]
        elif d['F'] == 2:
          raise Error.BUFRError('F 2 is called')
        elif d['F'] == 3:
          l = self.__tableD[k]['vals'][:]
          l.extend(proc)
          proc = l[:]
        else:
          raise Error.BUFRError('Unknown')
      ret.append(da)
    return ret

  def __read_section0(self):
    """
    Section0

    1 - 4: BUFR
    5 - 7: Total length
    8    : Edition No.
    """
    indicator = self.__read_octet(4, _arg_type['string'])
    if indicator != 'BUFR':
      raise Error.BUFRError('Not a BUFR file')
    self._section0['total_length'] = self.__read_octet(3, _arg_type['vint'])
    self._section0['version'] = self.__read_octet(1, _arg_type['uint8'])

  def __read_section1(self):
    """
    Section1

    1  -  3 : length of section
    4       : master table
    5  -  6 : centre (C-11)
    7  -  8 : sub-centre (C-12)
    9       : Update sequence
    10      : Optional Section
    11      : Data Category (Table A)
    12      : Sub Data Category (C-13)
    """
    self._section1['length'] = self.__read_octet(3, _arg_type['vint'])
    self._section1['master_table'] = self.__read_octet(1, _arg_type['uint8'])
    self._section1['centre'] = self.__read_octet(2, _arg_type['uint16'])
    self._section1['sub-centre'] = self.__read_octet(2, _arg_type['uint16'])
    self._section1['sequence'] = self.__read_octet(1, _arg_type['uint8'])
    is_sec2_v = self.__read_octet(1, _arg_type['uint8'])
    if is_sec2_v == 0:
      self._section1['include_sec2'] = False
    elif is_sec2_v == 128: # b1000000
      self._section1['include_sec2'] = True
    else:
      self._section1['include_sec2'] = None
    self._section1['data-category'] = self.__read_octet(1, _arg_type['uint8'])
    self._section1['sub-data-category'] = self.__read_octet(1, _arg_type['uint8'])
    self._section1['local-data-sub-category'] = self.__read_octet(1, _arg_type['uint8'])
    self._section1['master-table-version'] = self.__read_octet(1, _arg_type['uint8'])
    self._section1['local-table-version'] = self.__read_octet(1, _arg_type['uint8'])
    year = self.__read_octet(2, _arg_type['uint16'])
    month = self.__read_octet(1, _arg_type['uint8'])
    day = self.__read_octet(1, _arg_type['uint8'])
    hour = self.__read_octet(1, _arg_type['uint8'])
    minute = self.__read_octet(1, _arg_type['uint8'])
    second = self.__read_octet(1, _arg_type['uint8'])
    self._section1['time'] = datetime.datetime(year, month, day, hour, minute, second)
    self.__read_table()

    if self._section1['length'] == 22:
      return
    if self.__sec1func is not None:
      self.__sec1func()
    else:
      self.__read_octet(self._section1['length'] - 22, None)

  def __read_section2(self):
    """
    1 - 3 : length of section
    4     : Reserved (=0)
    5 -
    """
    if self._section1['include_sec2'] is False:
      return
    if self.__sec2func is not None:
      self.__sec2func()
    else:
      self._section2['length'] = self.__read_octet(3, _arg_type['vint'])
      r = self.__read_octet(1, _arg_type['uint8'])
      _ = self.__read_octet(self._section2['length'] - 4, None)

  def __read_section3(self):
    """
    1 - 3 : length of section
    4     : Reserved (=0)
    5 - 6 : Number of data sub set
    7     : data type
    8 -
    """
    self._section3['length'] = self.__read_octet(3, _arg_type['vint'])
    r = self.__read_octet(1, _arg_type['uint8'])
    if r != 0:
      raise Error.BUFRError('Section3 format is ignore')
    self._section3['subsets'] = self.__read_octet(2, _arg_type['uint16'])
    b = self.__read_octet(1, _arg_type['uint8'])
    obs = 128
    comp = 64
    if b == 0:
      self._section3['is_observation'] = False
      self._section3['is_compress'] = False
    elif b == obs:
      self._section3['is_observation'] = True
      self._section3['is_compress'] = False
    elif b == comp:
      self._section3['is_observation'] = False
      self._section3['is_compress'] = True
    elif b == (comp + obs):
      self._section3['is_observation'] = True
      self._section3['is_compress'] = True
    rest = self._section3['length'] - 7
    while rest > 0:
      F, X, Y  = self.__read_octet(2, _arg_type['description'])
      rest -= 2
      self._section3['description'].append({'F': F, 'X': X, 'Y': Y})

  def __read_section4(self):
    """
    1 - 3 : length of section
    4     : Reserved (=0)
    5 -   :
    """
    if self._section3['is_compress'] is True:
      raise Error.BUFRError('Compress BUFR Not Implemented')
    self._section4['length'] = self.__read_octet(3, _arg_type['vint'])
    r = self.__read_octet(1, _arg_type['uint8'])
    if r != 0:
      raise Error.BUFRError('Section4 format is ignore')

    rest = self._section4['length'] - 4
    buf = self.__read_octet(rest, None)
    self._section4['data'] = self.__read_data(buf)

  def __read_section5(self):
    """
    1 - 4: 7777
    """
    indicator = self.__read_octet(4, _arg_type['string'])
    if indicator != '7777':
      raise Error.BUFRError('Unknown Format')

  def open(self, filename):
    self.__fp = open(filename, 'rb')

  def close(self):
    self.__fp.close()

  def read(self):
    self.__read_section0()
    self.__read_section1()
    self.__read_section2()
    self.__read_section3()
    self.__read_section4()
    self.__read_section5()
