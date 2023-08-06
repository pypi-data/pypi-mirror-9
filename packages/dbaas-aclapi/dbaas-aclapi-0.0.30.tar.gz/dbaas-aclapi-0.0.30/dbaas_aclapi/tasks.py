from dbaas_aclapi.acl_base_client import AclClient
from dbaas_credentials.models import CredentialType
from dbaas_aclapi.models import DatabaseBind
from dbaas_aclapi.models import DatabaseInfraInstanceBind
from dbaas_aclapi.models import ERROR
from dbaas_cloudstack.models import DatabaseInfraAttr
from notification.models import TaskHistory
from celery import shared_task
import logging
from time import sleep
from simple_audit.models import AuditRequest

logging.basicConfig()
LOG = logging.getLogger("AclTask")
LOG.setLevel(logging.DEBUG)

@shared_task(bind=True)
def bind_address_on_database(self, database_bind, user=None):
    if not user:
        user =  self.request.args[-1]

    action="permit"
    LOG.info("User: {}, action: {}".format(user, action))

    worker_name = get_worker_name()
    task_history = TaskHistory.register(request=self.request, user=user,
        worker_name=worker_name)
    LOG.info("id: %s | task: %s | kwargs: %s | args: %s" % (self.request.id,
        self.request.task, self.request.kwargs, str(self.request.args)))
    task_history.update_details(persist=True, details="Loading Process...")
    database = database_bind.database

    try:
        acl_environment, acl_vlan = database_bind.bind_address.split('/')
        data = {"kind":"object#acl", "rules":[]}
        default_options = {"protocol": "tcp",
                                     "source": "",
                                     "destination": "",
                                     "description": "{} access for database {} in {}".\
                                     format(database_bind.bind_address, database.name,
                                      database.environment.name),
                                     "action": action,
                                     "l4-options":{ "dest-port-start":"",
                                                          "dest-port-op":"eq"
                                                          }
                                     }

        LOG.info("Default options: {}".format(default_options))
        databaseinfra = database.infra
        instances = databaseinfra.instances.all()
        port = instances[0].port

        for instance in instances:
            custom_options = default_options
            custom_options['source'] = database_bind.bind_address
            custom_options['destination'] = instance.address + '/32'
            custom_options['l4-options']['dest-port-start'] = instance.port
            data['rules'].append(custom_options)

            LOG.debug("Creating bind for instance: {}".format(instance))

            instance_bind = DatabaseInfraInstanceBind(instance= instance.address,
                databaseinfra= databaseinfra, bind_address= database_bind.bind_address,
                instance_port = instance.port)
            instance_bind.save()

            LOG.debug("InstanceBind: {}".format(instance_bind))

        LOG.debug("Instance binds created!")

        for instance in DatabaseInfraAttr.objects.filter(databaseinfra= databaseinfra):
            custom_options = default_options
            custom_options['source'] = database_bind.bind_address
            custom_options['destination'] = instance.ip + '/32'
            custom_options['l4-options']['dest-port-start'] = port
            data['rules'].append(custom_options)

            LOG.debug("Creating bind for instance: {}".format(instance))

            instance_bind = DatabaseInfraInstanceBind(instance= instance.address,
                databaseinfra= databaseinfra, bind_address= database_bind.bind_address,
                instance_port = port)
            instance_bind.save()

            LOG.debug("DatabaseInraAttrInstanceBind: {}".format(instance_bind))


        acl_credential = get_credentials_for(environment= database.environment,
            credential_type=CredentialType.ACLAPI)
        acl_client = AclClient(acl_credential.endpoint, acl_credential.user,
            acl_credential.password)

        LOG.info("Data used on payload: {}".format(data))
        response = acl_client.grant_acl_for(environment= acl_environment,
            vlan= acl_vlan, payload=data)

        monitor_acl_job(job= response['job'], database_bind= database_bind,
         user=user)
        return

    except Exception,e:
        LOG.info("DatabaseBind ERROR: {}".format(e))
        task_history.update_status_for(TaskHistory.STATUS_ERROR,
            details='Bind could not be created')

        DatabaseBind.objects.filter(id= database_bind.id,
            ).update(bind_status= ERROR)

        DatabaseInfraInstanceBind.objects.filter(databaseinfra= databaseinfra,
            bind_address= database_bind.bind_address,
            ).update(bind_status= ERROR)

        return

    finally:
        AuditRequest.cleanup_request()


@shared_task(bind=True)
def unbind_address_on_database(self, database_bind, user=None):
    if not user:
        user =  self.request.args[-1]

    action="deny"
    LOG.info("User: {}, action: {}".format(user, action))

    worker_name = get_worker_name()
    task_history = TaskHistory.register(request=self.request, user=user,
        worker_name=worker_name)
    LOG.info("id: %s | task: %s | kwargs: %s | args: %s" % (self.request.id,
        self.request.task, self.request.kwargs, str(self.request.args)))
    task_history.update_details(persist=True, details="Loading Process...")
    database = database_bind.database

    try:
        acl_environment, acl_vlan = database_bind.bind_address.split('/')
        data = {"kind":"object#acl", "rules":[]}
        default_options = {"protocol": "tcp",
                                     "source": "",
                                     "destination": "",
                                     "description": "{} access for database {} in {}".\
                                     format(database_bind.bind_address, database.name,
                                      database.environment.name),
                                     "action": action,
                                     "l4-options":{ "dest-port-start":"",
                                                          "dest-port-op":"eq"
                                                          }
                                     }

        LOG.info("Default options: {}".format(default_options))
        databaseinfra = database.infra
        infra_instances_binds = DatabaseInfraInstanceBind.objects.\
            filter(databaseinfra= databaseinfra,bind_address= database_bind.bind_address)

        for infra_instance_bind in infra_instances_binds:
            custom_options = default_options
            custom_options['source'] = database_bind.bind_address
            custom_options['destination'] = infra_instance_bind.instance + '/32'
            custom_options['l4-options']['dest-port-start'] = infra_instance_bind.instance_port
            data['rules'].append(custom_options)


        acl_credential = get_credentials_for(environment= database.environment,
            credential_type=CredentialType.ACLAPI)
        acl_client = AclClient(acl_credential.endpoint, acl_credential.user,
            acl_credential.password)

        LOG.info("Data used on payload: {}".format(data))
        acl_client.revoke_acl_for(environment= acl_environment,
            vlan= acl_vlan, payload=data)

        infra_instances_binds.delete()
        database_bind.delete()

        return

    except Exception,e:
        LOG.info("DatabaseBind ERROR: {}".format(e))
        task_history.update_status_for(TaskHistory.STATUS_ERROR,
            details='Bind could not be created')

        return

    finally:
        AuditRequest.cleanup_request()


def monitor_acl_job(self, job_id, bind_address, user=None, retries=6, wait=30, interval=40):
    try:
        database = bind_address.database
        LOG.debug("job_id: {}, bind_address: {}, user: {}".format(job_id, bind_address, user))
        acl_credential = get_credentials_for(environment= database.environment,
            credential_type=CredentialType.ACLAPI)

        acl_client = AclClient(acl_credential.endpoint, acl_credential.user,
            acl_credential.password)

        for attempt in range(retries):
            response = acl_client.get_job(job_id= job_id)
            if 'jobs' in response:
                status = response['jobs']['status']
                if status != "SUCCESS":
                    acl_client.run_job(job_id=job_id)
                else:
                    return True
            else:
                return False

            if attempt == retries-1:
                LOG.error("Maximum number of monitoring attempts.")
                return False

            LOG.info("Wating %i seconds to try again..." % ( interval))
            sleep(interval)

    except Exception, e:
        LOG.info("DatabaseBindMonitoring ERROR: {}".format(e))
        return False

    finally:
        AuditRequest.cleanup_request()




def get_credentials_for(environment, credential_type):
    from dbaas_credentials.models import Credential
    return Credential.objects.filter(integration_type__type= credential_type,
        environments= environment)[0]

def get_worker_name():
    from billiard import current_process
    p = current_process()
    return p.initargs[1].split('@')[1]
