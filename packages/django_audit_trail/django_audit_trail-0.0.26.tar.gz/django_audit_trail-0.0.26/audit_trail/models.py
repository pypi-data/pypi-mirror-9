# pylint: disable-msg=E1101,W0403,C0111,R0201
from collections import OrderedDict
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.module_loading import import_string

from jsonfield import JSONField

from utils import get_request


ENCODER_CLASS = DjangoJSONEncoder
if hasattr(settings, 'JSONFIELD_ENCODER'):
    ENCODER_CLASS = import_string(getattr(settings, 'JSONFIELD_ENCODER'))

dump_kwargs = {
    'cls': ENCODER_CLASS,
    'separators': (',', ':')
}


class AuditTrailQuerySet(models.QuerySet):
    def get_changes(self):
        changes_dict = {}
        if not self.exists():
            return {}

        model_class = self[0].content_type.model_class()

        for trail in self.order_by('id'):
            if not isinstance(trail.content_object, model_class):
                raise ValueError(
                    'AuditTrailQuerySet.get_changes couldn\'t get changes for different models: %s and %s' % (
                        model_class.__name__, trail.content_object.__class__.__name__
                    ))

            if trail.is_related_changed:
                continue

            self._apply_field_changes(changes_dict, trail)
        # Removing values that changed back
        # F.e. 1->2->3->1 should not be showed as change with 1->1
        for field, change in changes_dict.copy().items():
            if change['old_value'] == change['new_value']:
                del changes_dict[field]

        return changes_dict

    def get_related_changes(self):
        related_changes_dict = OrderedDict()
        changes = self.filter(action=AuditTrail.ACTIONS.RELATED_CHANGED).order_by('id')
        for change in changes:
            related_trail = change.related_trail
            key = '%s.%s-%d' % (
                related_trail.content_type.app_label,
                related_trail.content_type.name,
                int(related_trail.object_id)
            )

            related_object_changes = related_changes_dict.get(key, None)

            if related_object_changes is None:
                related_object_changes = {
                    'action': related_trail.get_action_display(),
                    'representation': related_trail.object_repr,
                    'changes': {},
                    'model': '%s.%s' % (related_trail.content_type.app_label, related_trail.content_type.model)
                }
                related_changes_dict[key] = related_object_changes

            if related_trail.is_deleted and related_object_changes['action'] == 'Created':
                del related_changes_dict[key]

            self._apply_field_changes(related_object_changes['changes'], related_trail)
        return related_changes_dict.values()

    def _apply_field_changes(self, changes_dict, trail):
        for field_name, field_change in trail.get_changes().items():
            if not field_name in changes_dict:
                changes_dict[field_name] = field_change
            changes_dict[field_name]['new_value'] = field_change['new_value']
            changes_dict[field_name]['field_name'] = field_name


class AuditTrailManager(models.Manager):
    def get_queryset(self):
        return AuditTrailQuerySet(self.model, using=self._db)

    def generate_for_instance(self, instance, action):
        audit_trail = self.model(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            object_repr=unicode(instance),
            action=action
        )

        request = get_request(['user', 'META'])
        if request:
            if request.user.is_authenticated():
                audit_trail.user = request.user
            audit_trail.user_ip = request.META.get('HTTP_X_FORWARDED_FOR', None) or request.META.get('REMOTE_ADDR')
        audit_trail.save()
        return audit_trail

    def generate_trail_for_instance_created(self, instance):
        return self.generate_for_instance(instance, AuditTrail.ACTIONS.CREATED)

    def generate_trail_for_instance_updated(self, instance):
        return self.generate_for_instance(instance, AuditTrail.ACTIONS.UPDATED)

    def generate_trail_for_instance_deleted(self, instance):
        return self.generate_for_instance(instance, AuditTrail.ACTIONS.DELETED)

    def generate_trail_for_related_change(self, instance):
        return self.generate_for_instance(instance, AuditTrail.ACTIONS.RELATED_CHANGED)


class AuditTrail(models.Model):
    class ACTIONS(object):
        CREATED = 1
        UPDATED = 2
        DELETED = 3
        RELATED_CHANGED = 4

    ACTION_CHOICES = (
        (ACTIONS.CREATED, 'Created'),
        (ACTIONS.UPDATED, 'Updated'),
        (ACTIONS.DELETED, 'Deleted'),
        (ACTIONS.RELATED_CHANGED, 'Related changed')
    )

    """ Table to store all changes of subscribed models. """
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.TextField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, blank=True, null=True)
    user_ip = models.IPAddressField(null=True)

    object_repr = models.CharField(max_length=200)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    action_time = models.DateTimeField(auto_now=True)

    # pylint: disable-msg=E1123
    changes = JSONField(dump_kwargs=dump_kwargs)

    related_trail = models.ForeignKey(to='self', null=True)

    objects = AuditTrailManager()

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u'%s was %s at %s' % (self.object_repr, self.get_action_display().lower(), self.action_time.isoformat())

    @property
    def is_created(self):
        return self.action == self.ACTIONS.CREATED

    @property
    def is_updated(self):
        return self.action == self.ACTIONS.UPDATED

    @property
    def is_deleted(self):
        return self.action == self.ACTIONS.DELETED

    @property
    def is_related_changed(self):
        return self.action == self.ACTIONS.RELATED_CHANGED

    def get_changes(self):
        if not isinstance(self.changes, dict):
            return self.changes

        changes = self.changes.copy()
        model_class = self.content_type.model_class()
        for field_name, change in changes.items():
            change['field_label'] = model_class._meta.get_field(field_name).verbose_name.capitalize()
        return changes