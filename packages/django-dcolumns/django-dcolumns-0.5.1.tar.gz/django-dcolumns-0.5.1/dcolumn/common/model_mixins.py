#
# dcolumn/common/model_mixins.py
#

"""
Mixins used in Django models.

by: Carl J. Nobile

email: carl.nobile@gmail.com
"""
__docformat__ = "restructuredtext en"

import re
import logging
from datetime import datetime
from dateutil.tz import tzutc

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from dcolumn.common import ChoiceManagerImplementation

log = logging.getLogger('dcolumn.models')


#
# UserModel
#
class UserModelMixin(models.Model):
    """
    Abstract model mixin used in the model classes to provide user and
    creator fields.
    """

    updater = models.ForeignKey(
        User, verbose_name=_("Updater"), db_index=True, editable=False,
        related_name="%(app_label)s_%(class)s_updater_related",
        help_text=_("The last user to update this record."))
    creator = models.ForeignKey(
        User, verbose_name=_("Creator"), db_index=True, editable=False,
        related_name="%(app_label)s_%(class)s_creator_related",
        help_text=_("The user  who created this record."))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save is here to assure that save is executed throughout the MRO.
        """
        super(UserModelMixin, self).save(*args, **kwargs)

    def _updater_producer(self):
        """
        Primary use is in the admin class to supply the user's full name.
        """
        return self.updater.get_full_name()
    _updater_producer.short_description = _("Updater")

    def _creator_producer(self):
        """
        Primary use is in the admin class to supply the creator's full name.
        """
        return self.creator.get_full_name()
    _creator_producer.short_description = _("Creator")


#
# TimeModel
#
class TimeModelMixin(models.Model):
    """
    Abstract model mixin used in the model classes to supply created and
    updated fields.
    """

    created = models.DateTimeField(
        verbose_name=_("Date Created"),
        help_text=_("The date and time of creation."))
    updated = models.DateTimeField(
        verbose_name=_("Last Updated"),
        help_text=_("The date and time last updated."))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Permit the disabling of the created and updated date times.
        """
        if not kwargs.pop(u'disable_created', False) and self.created is None:
            self.created = datetime.now(tzutc())

        if not kwargs.pop(u'disable_updated', False):
            self.updated = datetime.now(tzutc())

        log.debug("kwargs: %s, created: %s, updated: %s",
                  kwargs, self.created, self.updated)
        super(TimeModelMixin, self).save(*args, **kwargs)


#
# StatusModel
#
class StatusModelManagerMixin(models.Manager):
    """
    Manager mixin for the StatusModelMixin abstract model.
    """

    def active(self, active=True):
        """
        Return as default only active database objects.

        :Parameters:
          active : `bool`
            If `True` return only active records else if `False` return
            non-active records. If `None` return all records.
        """
        query = []

        if active is not None:
            query.append(Q(active=active))

        return self.filter(*query)


class StatusModelMixin(models.Model):
    """
    Abstract model mixin used in the model classes to supply the active field.
    """

    active = models.BooleanField(
        verbose_name=_("Active"), default=True,
        help_text=_("If checked the record is active."))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save is here to assure that save is executed throughout the MRO.
        """
        super(StatusModelMixin, self).save(*args, **kwargs)


#
# BaseChoiceModelManager
#
class BaseChoiceModelManager(models.Manager, ChoiceManagerImplementation):

    def get_value_by_pk(self, pk, field=None):
        value = u''

        if int(pk) != 0:
            try:
                obj = self.get(pk=pk)
                value = getattr(obj, field)
            except self.model.DoesNotExist as e:
                log.error("Access to PK %s failed, %s", pk, e)

        return value

    def get_choices(self, field, comment=True):
        choices = [(obj.pk, getattr(obj, field)) for obj in self.all()]

        if comment:
            choices.insert(
                0, (0, _("Please choose a {}".format(self.model.__name__))))

        return choices
