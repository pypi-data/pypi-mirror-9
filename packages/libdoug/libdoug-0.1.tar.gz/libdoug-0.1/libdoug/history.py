# vim: set fileencoding=utf-8
# Pavel Odvody <podvody@redhat.com>
#
# libdoug - DOcker Update Guard
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
from libdoug.values import EmptyDiff

class ImageHistory(object):
	"""Object that holds a full list of tags of
	a given `repository`.

	:param images: `list` of `Image Dictionary`
	"""
	class Entry(object):
		"""Provides unique mapping/ordering of `Image Id`'s and `tag`'s.

		:param tag: `string`, A tag
		:param imgid: `string`, An image id
		"""
		def __init__(self, tag, imgid):
			self.tag = tag
			self.id = imgid

		def gettag(self):
			return self.tag

		def getid(self):
			return self.id

		def __repr__(self):
			""" Prints as `tag` : `id` """
			return "%s : %s" % (self.gettag(), self.getid())
 
		def __eq__(self, other):
			""" Equal if both parts are same """
			return self.tag == other.tag and self.id == other.id

		def __hash__(self):
			""" Concats `tag` and `id` and from that computes the hash """
			return hash(self.tag + self.id)

		def __gt__(self, other):
			""" We order only by tags """
			return cmp(self.tag, other.tag) == 1


	def __init__(self, images):
		self.images = []
		self._addimages(images)

	@staticmethod
	def fromjson(json):
		"""Parse :class:`ImageHistory` from `json`

		:param json: `json object` of `tag`, `id` pairs
		:return: :class:`ImageHistory` object with the parsed history
		"""
		hist = ImageHistory([])
		for k, v in json.iteritems():
			hist.images.append(ImageHistory.Entry(k, v))		
		return hist

	def _addimages(self, images):
		for img in images:
			for repotag in img['RepoTags']:
				self.images.append(
					self.Entry(repotag.split(':')[1], img['Id'])
				)

	def getimages(self):
		""" A `list` of :class:`Entry` entries """
		return self.images

	def printout(self):
		""" Print all :class:`Entry` entries """
		for n, img in enumerate(sorted(self.images)):
			print "  %s" % (img)


class HistoryDiff(object):
	"""Compute a diff between two :class:`ImageHistory` objects

	:param a: :class:`ImageHistory` A side
	:param b: :class:`ImageHistory` B side
	"""
	def __init__(self, a, b):
		self.a = a
		self.b = b

	def diff(self):
		"""Compute the diff between `A` and `B`

		:return: `tuple of lists` of :class:`Entry` object, or :class:`libdoug.values.EmptyDiff`
		"""
		a, b = set(self.a.getimages()), set(self.b.getimages())
		if a == b:
			return EmptyDiff

		return (list(a - b), list(b - a))

	@staticmethod
	def printout(delta):
		""" Print value as returned by :meth:`diff` (sorted) """
		left, right = delta
		if left:
			print '\n'.join(['  L '+str(i) for i in sorted(list(left))])
		
		if right:
			print '\n'.join(['  R '+str(i) for i in sorted(list(right))])
