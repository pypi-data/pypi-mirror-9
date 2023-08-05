from mptt.models import MPTTModel


class PolicyManager(object):
    """
    PolcityManager provides functionality over node where from was constructed
    """
    model = None
    policy_class = None

    def __init__(self, model):
        if not isinstance(model, MPTTModel):
            msg = 'Model {} must be instance of MPTTModel'
            raise RuntimeError(msg.format(model.__class__))
        self.model = model
        self.policy_class = self.model._policy_class
        self.policy_meta = self.policy_class._policy_meta

        self.policy_related_name = self.policy_class._meta. \
            get_field('subject').rel.related_name

    def allow(self, role, principal):
        """
        Adds policy to principal with given role and apply rules

        :param role:
        :param principal:
        :return:
        """

        role_class = self.policy_meta.get_role(role)
        rules = role_class.rules

        for rule_class in rules:
            rule = rule_class(role_class)
            rule.apply(principal, self.model)

    def revoke_all(self, principal):
        """
        Removes role on node for given principal

        :param principal:
        :return:
        """
        rules = self.policy_meta.deletion_rules

        for rule_class in rules:
            rule = rule_class()
            rule.apply(principal, self.model)

    def initialize(self, principal):
        """
        Create empty policy for each node for given principal

        :param principal:
        :return:
        """
        return self.policy_class.objects.create(subject=self.model,
                                                principal=principal)

    def initialize_node(self):
        """
        Initialize empty policy for each user

        :return:
        """
        for principal in self.policy_class.get_principals_queryset():
            if self.policy_class.objects.filter(principal=principal, subject=self.model).exists():
                break
            self.initialize(principal)

    def insert(self, created):
        """
        This method is called whenever node is saved

        :return:
        """
        owner = getattr(self.model, 'acl_principal', None)

        if created:
            self.initialize_node()

        if not owner:
            return

        insertion_rules = self.policy_meta.insertion_rules

        for rule_class in insertion_rules:
            rule = rule_class()
            rule.apply(owner, self.model)

        if self.model.moved():
            rules = self.policy_meta.move_rules
            for rule_class in rules:
                rule = rule_class()
                rule.apply(owner, self.model)

    def delete(self):
        """
        This method is called whenever node will be deleted

        :return:
        """
        deletion_rules = self.policy_meta.deletion_rules

        owner = getattr(self.model, 'acl_principal', None)
        assert owner

        for rule_class in deletion_rules:
            rule = rule_class()
            rule.apply(owner, self.model)

    def has_permission(self, permission, principal):
        """
        Ask whether principal has given permission on the node

        :param permission:
        :param principal:
        :return:
        """
        policies = getattr(self.model, self.policy_related_name)
        policy = policies.get(principal=principal, subject=self.model)
        mask = getattr(policy.mask, permission)

        return bool(mask)

    def add_permissions_all(self, permissions, principal):

        policy = self.policy_for_principal(principal)

        for permission in permissions:
            policy.mask |= getattr(self.policy_class.mask, permission)

        policy.save()

    def add_permission(self, permission, principal):
        policy = self.policy_for_principal(principal)
        policy.mask |= getattr(self.policy_class.mask, permission)
        policy.save()

    def policy_for_principal(self, principal):
        policies = getattr(self.model, self.policy_related_name)
        return policies.get(principal=principal)

    def policies(self):
        return getattr(self.model, self.policy_related_name)

    def get_principals(self):

        policies = getattr(self.model, self.policy_related_name)
        policies = policies.filter(subject=self.model).select_related('principal')

        return map(lambda policy: policy.principal, policies)

    def get_roles(self, principal):
        policy = self.policies().get(principal=principal)
        return {role: policy.role == role
                for role in self.policy_meta.get_role_names()}

    def get_role_names(self):
        return self.policy_meta.get_role_names()

    def get_permissions(self, principal):
        policy = self.policies().get(principal=principal)
        return {str(perm): bool(getattr(policy.mask, perm))
                for perm in self.policy_meta.permissions}

    def _get_role_rules(self, role):
        """

        :type role: unicode
        :rtype: django-mptt-acl.rules.Rule[]
        """
        meta = self.policy_class._policy_meta
        return meta.get_role(role).rules
