#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Table models and functionality for the BANCA database.
"""

import os, numpy
import bob.db.base.utils
from sqlalchemy import Table, Column, Integer, String, ForeignKey, or_, and_
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.verification.utils

Base = declarative_base()

subworld_client_association = Table('subworld_client_association', Base.metadata,
  Column('subworld_id', Integer, ForeignKey('subworld.id')),
  Column('client_id',  Integer, ForeignKey('client.id')))

protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('file_id',  Integer, ForeignKey('file.id')))

class Client(Base):
  """Database clients, marked by an integer identifier and the group they belong to"""

  __tablename__ = 'client'

  # Key identifier for the client
  id = Column(Integer, primary_key=True)
  # Gender to which the client belongs to
  gender_choices = ('m','f')
  gender = Column(Enum(*gender_choices))
  # Group to which the client belongs to
  group_choices = ('g1','g2','world')
  sgroup = Column(Enum(*group_choices)) # do NOT use group (SQL keyword)
  # Language spoken by the client
  language_choices = ('en',)
  language = Column(Enum(*language_choices))

  def __init__(self, id, gender, group, language):
    self.id = id
    self.gender = gender
    self.sgroup = group
    self.language = language

  def __repr__(self):
    return "Client(%d, '%s', '%s', '%s')" % (self.id, self.gender, self.sgroup, self.language)

class Subworld(Base):
  """Database clients belonging to the world group are split in two disjoint subworlds,
     onethird and twothirds"""

  __tablename__ = 'subworld'

  # Key identifier for this Subworld object
  id = Column(Integer, primary_key=True)
  # Subworld to which the client belongs to
  name = Column(String(20), unique=True)

  # for Python: A direct link to the client
  clients = relationship("Client", secondary=subworld_client_association, backref=backref("subworld", order_by=id))

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Subworld('%s')" % (self.name)

class File(Base, bob.db.verification.utils.File):
  """Generic file container"""

  __tablename__ = 'file'

  # Key identifier for the file
  id = Column(Integer, primary_key=True)
  # Key identifier of the client associated with this file
  client_id = Column(Integer, ForeignKey('client.id')) # for SQL
  # Unique path to this file inside the database
  path = Column(String(100), unique=True)
  # Identifier of the claimed client associated with this file
  claimed_id = Column(Integer) # not always the id of an existing client model -> not a ForeignKey
  # Identifier of the shot
  shot_id = Column(Integer)
  # Identifier of the session
  session_id = Column(Integer)

  # For Python: A direct link to the client object that this file belongs to
  real_client = relationship("Client", backref=backref("files", order_by=id))
  annotation = relationship("Annotation", backref=backref("file"), uselist=False)

  def __init__(self, client_id, path, claimed_id, shot_id, session_id):
    # call base class constructor
    bob.db.verification.utils.File.__init__(self, client_id = client_id, path = path)

    self.claimed_id = claimed_id
    self.shot_id = shot_id
    self.session_id = session_id

class Annotation(Base):
  """Annotations of the BANCA database consists only of the left and right eye positions.
  There is exactly one annotation for each file."""
  __tablename__ = 'annotation'

  id = Column(Integer, primary_key=True)
  file_id = Column(Integer, ForeignKey('file.id'))

  le_x = Column(Integer) # left eye
  le_y = Column(Integer)
  re_x = Column(Integer) # right eye
  re_y = Column(Integer)

  def __init__(self, file_id, eyes):
    self.file_id = file_id

    assert len(eyes) == 4
    self.re_x = int(eyes[0])
    self.re_y = int(eyes[1])
    self.le_x = int(eyes[2])
    self.le_y = int(eyes[3])

  def __call__(self):
    """Returns the annotations of this database in a dictionary: {'reye' : (re_y, re_x), 'leye' : (le_y, le_x)}."""
    return {'reye' : (self.re_y, self.re_x), 'leye' : (self.le_y, self.le_x) }

  def __repr__(self):
    return "<Annotation('%s': 'reye'=%dx%d, 'leye'=%dx%d)>" % (self.file_id, self.re_y, self.re_x, self.le_y, self.le_x)


class Protocol(Base):
  """BANCA protocols"""

  __tablename__ = 'protocol'

  # Unique identifier for this protocol object
  id = Column(Integer, primary_key=True)
  # Name of the protocol associated with this object
  name = Column(String(20), unique=True)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % (self.name,)

class ProtocolPurpose(Base):
  """BANCA protocol purposes"""

  __tablename__ = 'protocolPurpose'

  # Unique identifier for this protocol purpose object
  id = Column(Integer, primary_key=True)
  # Id of the protocol associated with this protocol purpose object
  protocol_id = Column(Integer, ForeignKey('protocol.id')) # for SQL
  # Group associated with this protocol purpose object
  group_choices = ('world', 'dev', 'eval')
  sgroup = Column(Enum(*group_choices))
  # Purpose associated with this protocol purpose object
  purpose_choices = ('train', 'enroll', 'probe')
  purpose = Column(Enum(*purpose_choices))

  # For Python: A direct link to the Protocol object that this ProtocolPurpose belongs to
  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  # For Python: A direct link to the File objects associated with this ProtcolPurpose
  files = relationship("File", secondary=protocolPurpose_file_association, backref=backref("protocolPurposes", order_by=id))

  def __init__(self, protocol_id, sgroup, purpose):
    self.protocol_id = protocol_id
    self.sgroup = sgroup
    self.purpose = purpose

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.sgroup, self.purpose)

