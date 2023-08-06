# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2013/09/22
# copy: (C) Copyright 2013-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import unittest
import pxml
import xml.etree.ElementTree as ET
import six

import asset

#------------------------------------------------------------------------------
class TestAsset(unittest.TestCase, pxml.XmlTestMixin):

  maxDiff = None

  #----------------------------------------------------------------------------
  def test_version(self):
    self.assertRegexpMatches(asset.version('pxml'), r'^\d+.\d+.\d+$')

  #----------------------------------------------------------------------------
  def test_load_multi(self):
    self.assertEqual(len(asset.load('asset:test/data/file1.nl')), 1)
    self.assertEqual(
      [str(ast) for ast in asset.load('asset:test/data/file1.nl')],
      ['asset:test/data/file1.nl'])
    self.assertEqual(
      [str(ast) for ast in asset.load('asset:test/data/**.nl')],
      ['asset:test/data/file1.nl',
       'asset:test/data/file2.nl',
       'asset:test/data/subdir/subfile1.nl'])
    self.assertEqual(
      [ast.read() for ast in asset.load('asset:test/data/**.nl')],
      [b'line-1\nline-2',
       b'line-3\n',
       b'sub-file-line-1\n'])

  #----------------------------------------------------------------------------
  def test_load_single(self):
    loaded = []
    for item in asset.load('asset:test/data/file1.nl'):
      loaded.append(item)
    self.assertEqual(len(loaded), 1)
    self.assertEqual(loaded[0].package, 'asset')
    self.assertEqual(loaded[0].name, 'test/data/file1.nl')
    with self.assertRaises(asset.NoSuchAsset) as cm:
      asset.load('asset:no-such-file.ext').peek()

  #----------------------------------------------------------------------------
  def test_load_group_read(self):
    self.assertEqual(
      asset.load('asset:test/data/file1.nl').read(), b'line-1\nline-2')
    self.assertEqual(
      asset.load('asset:test/data/file2.nl').read(), b'line-3\n')
    self.assertEqual(
      asset.load('asset:test/data/*.nl').read(), b'line-1\nline-2line-3\n')
    ag = asset.load('asset:test/data/*.nl')
    self.assertEqual(ag.readline(), b'line-1\n')
    self.assertEqual(ag.readline(), b'line-2')
    self.assertEqual(ag.readline(), b'line-3\n')

  #----------------------------------------------------------------------------
  def test_load_example(self):
    out = ET.Element('nodes')
    for item in asset.load('asset:test/data/**.nl'):
      cur = ET.SubElement(out, 'node', name=item.name)
      cur.text = item.read().decode()
    out = ET.tostring(out)
    chk = b'''\
<nodes>
  <node name="test/data/file1.nl">line-1
line-2</node>
  <node name="test/data/file2.nl">line-3
</node>
  <node name="test/data/subdir/subfile1.nl">sub-file-line-1
</node>
</nodes>
'''
    self.assertXmlEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_listres(self):
    self.assertEqual(
      list(asset.listres('asset', 'test/data', showDirs=True)),
      [
        'test/data/file1.nl',
        'test/data/file2.nl',
        'test/data/subdir/',
        'test/data/subdir/subfile1.nl',
      ])

  #----------------------------------------------------------------------------
  def test_filename(self):
    # NOTE: this requires that `pxml` was installed as a zipped egg, and
    # `globre` as an UNzipped egg, i.e.:
    #   easy_install --zip-ok pxml
    #   easy_install --always-unzip globre
    for item in asset.load('globre:__init__.py'):
      self.assertIsNotNone(item.filename)
    for item in asset.load('pxml:__init__.py'):
      self.assertIsNone(item.filename)

  #----------------------------------------------------------------------------
  def test_readWithSize(self):
    self.assertEqual(
      asset.load('asset:test/data/file**').stream().read(),
      b'line-1\nline-2line-3\n')
    self.assertEqual(
      asset.load('asset:test/data/file**').stream().read(1024),
      b'line-1\nline-2line-3\n')
    stream = asset.load('asset:test/data/file**').stream()
    self.assertEqual(stream.read(5), b'line-')
    self.assertEqual(stream.read(5), b'1\nlin')
    self.assertEqual(stream.read(5), b'e-2li')
    self.assertEqual(stream.read(3), b'ne-')
    self.assertEqual(stream.read(3), b'3\n')
    self.assertEqual(stream.read(3), b'')

  #----------------------------------------------------------------------------
  def test_streamIteration(self):
    stream = asset.load('asset:test/data/file**').stream()
    self.assertEqual(stream.readline(), b'line-1\n')
    self.assertEqual(stream.readline(), b'line-2')
    self.assertEqual(stream.readline(), b'line-3\n')
    self.assertEqual(stream.readline(), b'')
    stream = asset.load('asset:test/data/file**').stream()
    chk = list(reversed([
      b'line-1\n',
      b'line-2',
      b'line-3\n',
    ]))
    for line in stream:
      self.assertEqual(line, chk.pop())

  #----------------------------------------------------------------------------
  def test_csv(self):
    import csv
    lines  = [line.decode() for line in asset.load('asset:test/data.csv').stream()]
    reader = csv.reader(lines)
    self.assertEqual(six.next(reader), ['a', 'b', 'c'])
    self.assertEqual(six.next(reader), ['1', '2', '3'])
    with self.assertRaises(StopIteration):
      six.next(reader)


#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
