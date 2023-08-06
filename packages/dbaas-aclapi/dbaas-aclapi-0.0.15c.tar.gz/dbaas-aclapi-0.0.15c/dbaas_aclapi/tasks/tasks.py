from ..acl_base_client import AclClient
from util import get_credentials_for
from dbaas_credentials.models import CredentialType
from ..models import DatabaseBind, DatabaseInfraInstanceBind, CREATING
from dbaas_cloudstack.models import DatabaseInfraAttr
import logging
from time import sleep

logging.basicConfig()
LOG = logging.getLogger("AclTask")
LOG.setLevel(logging.DEBUG)

def bind_unbind_address_on_database(database, acl_environment, acl_vlan,
    action="permit", bind_status=CREATING):
    bind_address = "{}/{}".format(acl_environment, acl_vlan)

    data = {"kind":"object#acl", "rules":[]}

    default_options = {"protocol": "tcp",
                                 "source": "",
                                 "destination": "",
                                 "description": "{} access for database {} in {}".format(bind_address,
                                    database.name, database.environment.name),
                                 "action": action,
                                 "l4-options":{ "dest-port-start":"",
                                                      "dest-port-op":"eq"
                                                      }
                                 }

    LOG.info("Default options: {}".format(default_options))

    bind, created = DatabaseBind.objects.get_or_create(database= database,
                                                                                    bind_address= bind_address,
                                                                                    defaults={'bind_status': CREATING}
                                                                                    )
    LOG.debug("Bind: {}, created? {}".format(bind, created))

    if not created:
        bind.bind_status = bind_status
        bind.save()

    databaseinfra = database.infra
    instances = databaseinfra.instances.all()

    port = instances[0].port

    for instance in instances:
        custom_options = default_options
        custom_options['source'] = bind_address
        custom_options['destination'] = instance.address + '/32'
        custom_options['l4-options']['dest-port-start'] = port
        data['rules'].append(custom_options)

        LOG.debug("Creating bind for instance: {}".format(instance))

        bind_instance, created = DatabaseInfraInstanceBind.objects.\
        get_or_create(instance= instance.address,databaseinfra= databaseinfra,
                             bind_address= bind_address,defaults={'bind_status': CREATING}
                            )

        if not created:
            bind_instance.bind_status = bind_status
            bind_instance.save()

        LOG.debug("InstanceBind: {}, created? {}".format(bind_instance, created))

    for instance in DatabaseInfraAttr.objects.filter(databaseinfra= databaseinfra):
        custom_options = default_options
        custom_options['source'] = bind_address
        custom_options['destination'] = instance.ip + '/32'
        custom_options['l4-options']['dest-port-start'] = port
        data['rules'].append(custom_options)

        LOG.debug("Creating bind for instance: {}".format(instance))

        bind_instance, created = DatabaseInfraInstanceBind.\
        objects.get_or_create(instance= instance.ip,
                                         databaseinfra= databaseinfra,
                                         bind_address= bind_address,
                                         defaults={'bind_status': CREATING}
                                        )
        if not created:
            bind_instance.bind_status = bind_status
            bind_instance.save()


    acl_credential = get_credentials_for(environment= database.environment,
        credential_type=CredentialType.ACLAPI)
    acl_client = AclClient(acl_credential.endpoint, acl_credential.user,
        acl_credential.password)

    LOG.info("Data used on payload: {}".format(data))
    if bind.bind_status == CREATING:
        response = acl_client.grant_acl_for(environment= acl_environment,
            vlan= acl_vlan, payload=data)
    else:
        response = acl_client.revoke_acl_for(environment= acl_environment,
            vlan= acl_vlan, payload=data)


    if 'job' in response:
        LOG.info("Calling acl_job monitor...")
        return response['job']
    else:
        raise Exception('Request error {}'.format(response))


def monitor_acl_job(database, job_id, bind_address, retries=6, wait=30, interval=40):
    acl_credential = get_credentials_for(environment= database.environment,
        credential_type=CredentialType.ACLAPI)
    acl_client = AclClient(acl_credential.endpoint, acl_credential.user,
        acl_credential.password)


    for attempt in range(retries):
        response = acl_client.get_job(job_id= job_id)

        if 'jobs' in response:
            status = response['jobs']['status']
            if status == 'PENDING':
                sleep(60)
                acl_client.get_next_job()
            elif status == "SUCCESS":
                return True
            elif status == "ERROR":
                return False
        else:
            return False

        if attempt == retries-1:
            LOG.error("Maximum number of monitoring attempts.")
            return False

        LOG.info("Wating %i seconds to try again..." % ( interval))
        sleep(interval)
