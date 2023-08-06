# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
sys.path.append('/Users/jmcarp/code/guardian')

from django.db import models as dj
from django.contrib.auth.models import AbstractUser

from guardrail.core.registry import registry

from guardrail.ext.django.models import DjangoPermissionSchemaFactory


@registry.agent
class RoleGroup(dj.Model):
    pass


class Role(dj.Model):
    role_groups = dj.ManyToManyField(RoleGroup)


class User(AbstractUser):
    roles = dj.ManyToManyField(Role)


@registry.target
class Project(dj.Model):
    pass


@registry.target
class File(dj.Model):
    pass


class Label(dj.Model):
    file = dj.ForeignKey(File, related_name='labels')


factory = DjangoPermissionSchemaFactory((dj.Model, ))
registry.make_schemas(factory)
