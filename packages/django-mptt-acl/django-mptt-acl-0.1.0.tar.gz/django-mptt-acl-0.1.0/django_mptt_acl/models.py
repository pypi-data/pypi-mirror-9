from bitfield.models import BitField
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.fields import CharField, FieldDoesNotExist
from django.utils import six
from managers import PolicyManager
from rules import DefaultInsertionRule, DefaultMoveRule, \
    InheritInsertionRule, ClearDeletionRule, DefaultRoleRule
from .signals import on_node_saved, on_node_deleted
from django.db.models.signals import post_save, pre_delete
from django.core import checks


class ManageRole(object):
    name = 'manage'
    permissions = ('read', 'write', 'create')

    required_permissions_ancestors = ('read',)
    required_permissions_descendants = ('read', 'write', 'create')
    rules = (DefaultRoleRule,)


class WriteRole(object):
    name = 'write'
    permissions = ('read', 'write')

    required_permissions_ancestors = ('read',)
    required_permissions_descendants = ('read',)
    rules = (DefaultRoleRule,)


class ReadRole(object):
    name = 'read'
    permissions = ('read',)

    required_permissions_ancestors = ('read',)
    required_permissions_descendants = ('read',)
    rules = (DefaultRoleRule,)


class CreateRole(object):
    name = 'create'
    permissions = ('create', )
    required_permissions_ancestors = ('read',)
    required_permissions_descendants = []
    rules = (DefaultRoleRule,)


class PolicyMetaOptions(object):

    # permissions = ('read', 'write', 'create')
    roles = {
        'manage': ManageRole,
        'read': ReadRole,
        'create': CreateRole,
        'write': WriteRole
    }

    insertion_rules = (DefaultInsertionRule, InheritInsertionRule)
    deletion_rules = (ClearDeletionRule, )
    move_rules = (DefaultMoveRule, )
    subject_owner_field = 'owner'

    @property
    def permissions(self):
        r = []
        for key, val in self.roles.items():
            for perm in val.permissions:
                if perm not in r:
                    r.append(perm)
        return r

    def __init__(self, opts=None, **kwargs):
        if opts:
            opts = list(opts.__dict__.items())
        else:
            opts = []
        opts.extend(list(kwargs.items()))

        for key, value in opts:
            setattr(self, key, value)

    def __iter__(self):
        return ((k, v) for k, v in self.__dict__.items() if k[0] != '_')

    def has_role(self, role):
        """
        Does role exists

        :param role:
        :return:
        """
        return role in self.roles

    def get_role(self, role):
        """
        Return role class if exists, otherwise raise ValueError

        :param role:
        :return:
        """
        if not self.has_role(role):
            msg = 'Role {} does not exists. Available roles are {}'
            raise ValueError(msg.format(
                role, ', '.join(self.get_role_names())))

        return self.roles.get(role)

    def get_role_instance(self, role):
        """
        Return role class if exists, otherwise raise ValueError

        :param role:
        :return:
        """
        return self.roles.get(role)()

    def get_role_names(self):
        """
        Return list of role names

        :return:
        """
        return [name for name, klazz in self.roles.items()]


class PolicyModelBase(ModelBase):

    def __new__(cls, name, bases, attrs):

        super_new = super(PolicyModelBase, cls).__new__
        policy_meta = attrs.pop('PolicyMeta', None)

        if not policy_meta:
            class policy_meta:
                pass

        initial_options = frozenset(dir(policy_meta))
        # extend PolicyMeta from base classes
        for base in bases:
            if hasattr(base, '_policy_meta'):
                for name, value in base._policy_meta:
                    if name not in initial_options:
                        setattr(policy_meta, name, value)
        policy_meta = PolicyMetaOptions(policy_meta)
        attrs.update({'_policy_meta': policy_meta})

        # call super
        ret = super_new(cls, name, bases, attrs)
        if ret._meta.abstract:
            return ret

        try:
            ret._meta.get_field('mask')
        except models.FieldDoesNotExist:
            field = BitField(flags=policy_meta.permissions)
            field.contribute_to_class(ret, 'mask')

        subject = ret._meta.get_field('subject')
        cls.wrap_subject(subject.rel.to)

        cls._register_signals(subject.rel.to)
        setattr(subject.rel.to, '_policy_class', ret._meta.concrete_model)
        return ret

    @classmethod
    def wrap_subject(cls, subject):
        """
        Wrap model init method to add acl manager model instance and remember
        parent subject which was model inited. This used to determine
        whether subject was moved.

        :param subject:
        :return:
        """
        def init(self, *args, **kwargs):
            super(subject, self).__init__(*args, **kwargs)
            self._original_parent = self.parent
            self.acl = PolicyManager(self)

        subject.__init__ = init

        def moved(self):
            return self._original_parent != self.parent
        subject.moved = moved

    @classmethod
    def _register_signals(cls, subject_model):
        """
        Register Django db signals over the observed model

        :param subject_model:
        :return:
        """
        post_save.connect(on_node_saved, sender=subject_model)
        pre_delete.connect(on_node_deleted, sender=subject_model)


class PolicyModel(six.with_metaclass(PolicyModelBase, models.Model)):
    role = CharField(max_length=30, null=True)

    def get_role_class(self):
        return self._policy_meta.get_role(self.role)

    @classmethod
    def get_pericipal_model(cls):
        return cls._meta.get_field('principal').rel.to

    @classmethod
    def get_principals_queryset(cls):
        return cls.get_pericipal_model().objects.all()

    class Meta:
        abstract = True

    @classmethod
    def check(cls, **kwargs):
        """
        Django check framework method

        :param kwargs:
        :return:
        """
        errors = super(PolicyModel, cls).check(**kwargs)

        for field_name in ['mask', 'role', 'subject', 'principal']:
            try:
                cls._meta.get_field(field_name)
            except FieldDoesNotExist:
                msg = 'Field {} is missing on model {}'
                errors.extend([
                    checks.Error(
                        msg.format(field_name, cls.__class__.__name__),
                        hint='Field is added to model when model in '
                             'inited by default',
                        obj=cls,
                        id='django_mttp_acl.E001',
                    )])

        if not isinstance(getattr(cls, '_policy_meta', None), PolicyMetaOptions):
            errors.extend([
                checks.Error(
                    'PolicyMeta class is missing or in not child class of '
                    'django_mptt_acl.models.PolicyModel',
                    hint='Use PolicyMeta class as parent for your custom '
                         'policy meta class',
                    obj=cls,
                    id='django_mttp_acl.E002',
                )
            ])

        return errors
