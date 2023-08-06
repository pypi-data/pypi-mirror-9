# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from logical.models import Database
from physical.models import DatabaseInfra
import simple_audit

ERROR = 0
CREATED= 1
CREATING = 2
DESTROYING = 3

BIND_STATUS = (
    (DESTROYING, 'Destroying'),
    (CREATED, 'Created'),
    (CREATING, 'Creating'),
    (ERROR, 'Error')
)

class BaseModel(models.Model):
    """Base model class"""
    created_at = models.DateTimeField(verbose_name=_("created_at"),
        auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated_at"),
        auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        if hasattr(self, 'name'):
            return "%s" % self.name
        elif hasattr(self, '__unicode__'):
            return self.__unicode__()

class DatabaseBind(BaseModel):
    database =  models.ForeignKey(Database, related_name="acl_binds",
        on_delete=models.PROTECT, null=False, blank=False, editable=False)
    bind_address = models.GenericIPAddressField(verbose_name=_("Address"),
        null=False, blank=False, editable=False)
    bind_status = models.IntegerField(choices=BIND_STATUS, default=2)
    binds_requested = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = (
            ('database', 'bind_address', )
        )

    def __unicode__(self):
        return "{} access to {}".format(self.bind_address, self.database)


class DatabaseInfraInstanceBind(BaseModel):
    databaseinfra = models.ForeignKey(DatabaseInfra, related_name="acl_binds",)
    instance = models.GenericIPAddressField(verbose_name=_("Instance Address"),
        null=False, blank=False, editable=False)
    instance_port = models.PositiveSmallIntegerField(verbose_name=_("Instance Port"),
        null=False, blank=False, editable=False,)
    bind_address = models.GenericIPAddressField(verbose_name=_("Bind Address"),
        null=False, blank=False, editable=False)
    bind_status = models.IntegerField(choices=BIND_STATUS,default=2)

    class Meta:
        unique_together = (
            ('instance', 'instance_port', 'bind_address', 'databaseinfra')
        )

    def __unicode__(self):
        return "{} access to {}".format(self.bind_address, self.instance)

simple_audit.register(DatabaseInfraInstanceBind, DatabaseBind)
