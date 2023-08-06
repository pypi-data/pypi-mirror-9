from dbaas_aclapi.models import DatabaseBind, DatabaseInfraInstanceBind, CREATED, CREATING, ERROR
import logging

logging.basicConfig()
LOG = logging.getLogger("AclBindApi")
LOG.setLevel(logging.DEBUG)

def update_bind_status(database, bind_address, bind_status):

    LOG.debug("Update {} bind {} with status {}".format(database, bind_address, bind_status))

    if bind_status not in [CREATING, CREATED]:
        bind_status = ERROR
    else:
        bind_status = CREATED

    bind = DatabaseBind.objects.get(database= database, bind_address= bind_address)
    databaseinfra = database.databaseinfra
    bind_instances = DatabaseInfraInstanceBind.objects.filter(databaseinfra=databaseinfra,  bind_address= bind_address)

    if bind_status == 0:
        bind.delete()
        bind_instances.delete()
        return

    bind.status = bind_status
    bind.save()

    for bind_instance in bind_instances:
        bind_instance.status = bind_status
        bind_instance.save()

    return
