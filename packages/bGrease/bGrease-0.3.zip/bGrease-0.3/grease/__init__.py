#############################################################################
#
# Copyright (c) 2010 by Casey Duncan and contributors
# All Rights Reserved.
#
# This software is subject to the provisions of the MIT License
# A copy of the license should accompany this distribution.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#
#############################################################################

__versioninfo__ = (0, 3, 0)
__version__ = '.'.join(str(n) for n in __versioninfo__)

__all__ = ('BaseWorld', 'Entity', 'System', 'Renderer')

import component
import geometry
import collision
from entity import Entity
from world import BaseWorld

import abc

class System(object):
	"""Grease system abstract base class. Systems define behaviorial aspects
	of a |BaseWorld|. All systems must define a :meth:`step`
	method that is invoked by the world each timestep.  User-defined systems
	are not required to subclass this class.
	
	See :ref:`an example system from the tutorial <tut-system-example>`.
	"""
	__metaclass__ = abc.ABCMeta

	world = None
	"""The |BaseWorld| this system belongs to"""

	def set_world(self, world):
		"""Bind the system to a world"""
		self.world = world
	
	@abc.abstractmethod
	def step(self, dt):
		"""Execute a time step for the system. Must be defined
		by all system classes.

		:param dt: Time since last step invocation
		:type dt: float
		"""

class Renderer(object):
	"""Grease renderer abstract base class. Renderers define the presentation
	of a |BaseWorld|. All renderers must define a :meth:`draw`
	method that is invoked by the world when the display needs to be redrawn.
	User-defined renderers are not required to subclass this class.

	See :ref:`an example renderer from the tutorial <tut-renderer-example>`.
	"""
	__metaclass__ = abc.ABCMeta

	world = None
	"""The |BaseWorld| this renderer belongs to"""

	def set_world(self, world):
		"""Bind the system to a world"""
		self.world = world

	@abc.abstractmethod
	def draw(self):
		"""Issue drawing commands for this renderer. Must be defined
		for all renderer classes.
		"""

