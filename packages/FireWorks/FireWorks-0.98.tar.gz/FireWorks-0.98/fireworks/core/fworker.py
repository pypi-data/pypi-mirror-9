# coding: utf-8

from __future__ import unicode_literals

"""
This module contains FireWorker, which encapsulates information about a
computing resource
"""

import json
from fireworks.utilities.fw_serializers import FWSerializable, \
    recursive_serialize, recursive_deserialize, DATETIME_HANDLER

__author__ = 'Anubhav Jain'
__credits__ = 'Michael Kocher'
__copyright__ = 'Copyright 2012, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Dec 12, 2012'


class FWorker(FWSerializable):

    def __init__(self, name="Automatically generated Worker", category='',
                 query=None, env=None):
        """
        Args:
            name: the name of the resource, should be unique
            category: a String describing the computing resource, does not
                need to be unique
            query: a dict query that restricts the type of Firework this
                resource will run
            env: a dict of special environment variables for the resource.
                This env is passed to running FireTasks as a _fw_env in the
                fw_spec, which provides for abstraction of resource-specific
                commands or settings.  See
                :class:`fireworks.core.firework.FireTaskBase` for information
                on how to use this env variable in FireTasks.
        """
        self.name = name
        self.category = category
        self._query = query if query else {}
        self.env = env if env else {}

    @recursive_serialize
    def to_dict(self):
        return {'name': self.name, 'category': self.category,
                'query': json.dumps(self.query, default=DATETIME_HANDLER),
                'env': self.env}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        return FWorker(m_dict['name'], m_dict['category'],
                       json.loads(m_dict['query']),
                       m_dict.get("env"))

    @property
    def query(self):
        q = self._query
        q['$or'] = [{"spec._fworker": {"$exists": False}}, {"spec._fworker": None}, {"spec._fworker": self.name}]
        if self.category:
            q['spec._category'] = self.category
        return q
