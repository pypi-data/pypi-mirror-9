class Rule(object):
    def apply(self, principal, subject):
        raise NotImplemented('Method apply not implemented')

    def apply_ancestors(self, principal, subject):
        raise NotImplemented('Method apply_ancestors not implemented')

    def apply_descendants(self, principal, subject):
        raise NotImplemented('Method apply_ancestors not implemented')


class DefaultInsertionRule(Rule):
    """
    Adds default role to node for principal that created node.
    """
    default_role = 'manage'

    def apply(self, principal, subject):
        """
        Adds default role on subject to principal
        :param principal:
        :param subject: MPTTModel
        :return:
        """
        policy = subject.acl.policy_for_principal(principal)

        role_class = policy._policy_meta.roles.get(self.default_role)
        role_permissions = role_class.permissions
        policy.mask = None

        # @todo it would be nice to use some role rule for this
        for permission in role_permissions:
            policy.mask |= getattr(policy.__class__.mask, permission)

        policy.role = self.default_role
        policy.save()


class InheritInsertionRule(Rule):
    """
    Adds permissions to node base on permissions of parent node for all principals
    that have policy on parent node.
    """
    def apply(self, principal, subject):
        """
        copies policy permissions (not role) from parent of subject
        :param principal:
        :param subject:
        :return:
        """
        # @todo I think this will not work together with default insertion
        # @todo subject.parent is not known attribute name
        # rule - prove by integration test
        parent = subject.parent

        if subject.is_root_node():
            # root node, there is nothing to inherit from
            return

        for parent_policy in parent.acl.policies().all().exclude(principal=principal):
            principal = parent_policy.principal

            policy = subject.acl.policy_for_principal(principal)
            policy.mask = parent_policy.mask
            policy.save()


class ClearDeletionRule(Rule):
    """
    Removes all permissions and roles from nodes descending from node where
    role has been dropped.
    This rule is applied when role is removed from node for some principal.

    """
    def apply(self, principal, subject):
        """
        Clears all permissions and roles from descending nodes.
        :type principal:
        :type subject: mptt.models.MPTTModel
        :return:
        """
        self._clear_role_descending(principal, subject)

    def _clear_role_descending(self, principal, subject):
        """
        Clears role from subject and all its children
        :param principal:
        :param subject:
        :return:
        """
        children = subject.get_children()

        for child in children:
            self._clear_role_descending(principal, child)

        policy = subject.acl.policy_for_principal(principal)
        policy.role = None
        policy.mask = None
        policy.save()


class InheritDeletionRule(Rule):
    """
    Removes role from node and inherits permissions from the nearest ancestor
    with node.
    Applied when role is dropped from node.
    """
    def apply(self, principal, subject):
        """
        Clears permissions and roles on descendant nodes.
        :type principal:
        :type subject: mptt.models.MPTTModel
        :return:
        """

        parent = subject.parent
        subject_policy = subject.acl.policy_for_principal(principal)
        subject_policy.role = None

        while parent is not None:
            parent_policy = parent.acl.policy_for_principal(principal)
            if parent_policy.role is not None:
                subject_policy.mask = parent_policy.mask
                subject_policy.save()
                return
            parent = parent.parent


class ClearRepropagateDeletionRule(Rule):
    """
    Clears role and permissions and role from node and all its children until
    it finds child with role. Then role is re-propagated back up the tree.
    Applied when role is dropped from node.
    """
    def apply(self, principal, subject):

        self._clear_role_descending(principal, subject)

    def _clear_role_descending(self, principal, subject):
        """
        Clears role from subject and all its children
        :param principal:
        :type subject: mptt.models.MPTTModel
        :return:
        """
        # @todo there is some function that will retrieve all subnodes,
        # but it will change the way how this
        # method works
        children = subject.get_children()

        # important - has to be before cleaning is done for children
        # node can get some permissions back due to repropagation
        policy = subject.acl.policy_for_principal(principal)
        policy.mask = 0
        policy.role = None
        policy.save()

        # clean permissions for children
        for child in children:
            child_policy = child.acl.policy_for_principal(principal)

            if child_policy.role is not None:
                # repropagate role back up using defined rules
                # also stops descending down the tree
                rules = subject.acl._get_role_rules(child_policy.role)

                for rule_class in rules:
                    rule = rule_class()
                    rule.apply_ancestors(principal, child)
            else:
                self._clear_role_descending(principal, child)


class DefaultMoveRule(Rule):
    """
    Removes all permissions and roles from node and all its children.
    Applied when node is moved in tree (parent changes).
    """
    def apply(self, moving_principal, subject):
        """
        Removes all permissions for all principals except the one that performed
        move action.
        :type moving_principal: mptt.models.MPTTModel principal performing move action
        """
        principals = subject.acl.get_principals()

        descendants = subject.get_descendants(True)

        for descendant in descendants:
            for principal in principals:
                if principal.pk is not moving_principal.pk:
                    descendant.acl.revoke_all(principal)


class DefaultInheritMoveRule(Rule):

    def apply(self, principal, subject):
        pass
        # parent = subject.get_ancestors().first()


class DefaultRoleRule(Rule):
    """
    Adds permissions defined in role to node. Also ensures that all nodes up and down the tree
    have permissions necessary to work correctly.
    Rule applied when new role is assigned to node.
    """

    role = None

    def __init__(self, role=None):
        self.role = role

    def apply_ancestors(self, principal, subject):
        """
        Used when you need to propagate role permission only up the tree.
        :type principal: django.contrib.auth.models.User
        :type subject: mptt.models.MPTTModel
        :return:
        """
        ancestors = subject.get_ancestors()
        subject_policy = subject.acl.policy_for_principal(principal)
        permissions = subject_policy.get_role_class().\
            required_permissions_ancestors

        for ancestor in ancestors:
            policy = ancestor.acl.policy_for_principal(principal)
            if policy.role is None:
                ancestor.acl.add_permissions_all(permissions, principal)
            else:
                # stop with first node with some role
                break

    def apply(self, principal, subject):
        """
        Adds basic permission to all ancestors until it finds some role or
        until the end.

        :type principal:
        :type subject: mptt.models.MPTTModel
        :return:
        """
        # @todo reduce number of DB selects and updates

        nodes_to_process = list(subject.get_children())
        subject_policy = subject.acl.policy_for_principal(principal)
        subject_policy.role = self.role.name
        subject_policy.save()

        subject.acl.add_permissions_all(self.role.permissions, principal)

        apply_up_queue = [(subject, subject_policy)]

        # processes nodes from subject down
        while len(nodes_to_process) is not 0:

            node = nodes_to_process.pop()

            policy = node.acl.policy_for_principal(principal)

            if policy.role is None:
                # add permissions determined by starting node and add all
                # children for processing
                permissions = subject_policy.get_role_class().\
                    required_permissions_descendants
                node.acl.add_permissions_all(permissions, principal)
                nodes_to_process.extend(node.get_children())

            else:
                # enqueue role application back up and stop processing descendants
                apply_up = (node, policy)
                apply_up_queue.append(apply_up)

        for apply_up in apply_up_queue:
            node, descendant_policy = apply_up

            while True:
                node = node.parent

                node_without_role = node is not None and \
                    node.acl.policy_for_principal(principal).role is None

                if not node_without_role:
                    break

                permissions = descendant_policy.get_role_class().\
                    required_permissions_ancestors
                node.acl.add_permissions_all(permissions, principal)