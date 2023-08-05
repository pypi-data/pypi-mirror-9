
def on_node_saved(sender, instance, created, **kwargs):
    """
    Called whenever new record if observed tree inserted, or whenever
    is node updated. Instance is marked as moved when parent of instance
    was changed

    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if not getattr(instance, 'acl_propagation_stopped', False):
        instance.acl.insert(created=created)


def on_node_deleted(sender, instance, **kwargs):
    """
    Called whenever is record of node deleted

    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    instance.acl.delete()
