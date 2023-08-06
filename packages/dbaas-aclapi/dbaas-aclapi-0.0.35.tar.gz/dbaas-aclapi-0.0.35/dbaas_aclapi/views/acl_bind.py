# from rest_framework.views import APIView
# from rest_framework.renderers import JSONRenderer, JSONPRenderer
# from rest_framework.response import Response
# import logging
# from logical.models import Database
# from dbaas_aclapi.models import DatabaseBind
# from rest_framework import status
# from django.core.exceptions import ObjectDoesNotExist
# from notification.models import TaskHistory
# from dbaas_aclapi.tasks import bind_address_on_database
# from django.contrib.sites.models import Site
# import json

# logging.basicConfig()
# LOG = logging.getLogger("AclBindApi")
# LOG.setLevel(logging.DEBUG)

# class ServiceBind(APIView):
#     renderer_classes = (JSONRenderer, JSONPRenderer)
#     model = DatabaseBind

#     def get(self, request, database_id, format=None):
#         try:
#             database = Database.objects.get(id=database_id)
#         except ObjectDoesNotExist, e:
#             msg = "Database {} does not exist".format(database_id)
#             return log_and_response(msg=msg, e=e, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         binds = DatabaseBind.objects.filter(database=database).values('bind_address', 'bind_status')
#         LOG.debug("Binds: {}".format(binds))

#         if not binds:
#             msg = "Database {} has no binds.".format(database_id)
#             return log_and_response(msg=msg, http_status=status.HTTP_204_NO_CONTENT)

#         LOG.debug("Responding...")
#         return Response({'binds':binds}, status.HTTP_202_ACCEPTED)


#     def post(self, request, database_id, format=None):
#         data = request.DATA
#         LOG.debug("Request DATA {}".format(data))

#         user = request.user

#         try:
#             database = Database.objects.get(id = database_id)
#         except ObjectDoesNotExist, e:
#             msg = "Database {} does not exist.".format(database_id)
#             return log_and_response(msg=msg, e=e, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         task = TaskHistory.objects.filter(arguments__contains=database.name,
#              task_status="RUNNING",).order_by("created_at")

#         LOG.info("Task {}".format(task))
#         if task:
#             msg = "Database {} is beeing created.".format(database_id, )
#             return log_and_response(msg=msg, http_status=status.HTTP_412_PRECONDITION_FAILED)

#         if not(database and database.status):
#             msg = "Database {} is not Alive.".format(database_id)
#             return log_and_response(msg=msg, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         if (not 'bind_address' in data) or (not 'mask' in data):
#             msg = "Invalid Params for {}".format(database_id)
#             return log_and_response(msg=msg, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#         task = bind_address_on_database.delay(database, data['bind_address'], data['mask'], action="permit", user=user)

#         return Response(get_task_url(task.id),status.HTTP_201_CREATED)

#     def delete(self, request, database_id, format=None):
#         data = request.DATA
#         if type(data) == str:
#             data = json.loads(data)
#         LOG.debug("Request DATA {}".format(data))

#         user = request.user

#         try:
#             database = Database.objects.get(id = database_id)
#         except ObjectDoesNotExist, e:
#             msg = "Database {} does not exist.".format(database_id)
#             return log_and_response(msg=msg, e=e, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         task = TaskHistory.objects.filter(arguments__contains=database.name,
#              task_status="RUNNING",).order_by("created_at")

#         LOG.info("Task {}".format(task))
#         if task:
#             msg = "Database {} is beeing created.".format(database_id, )
#             return log_and_response(msg=msg, http_status=status.HTTP_412_PRECONDITION_FAILED)

#         if not(database and database.status):
#             msg = "Database {} is not Alive.".format(database_id)
#             return log_and_response(msg=msg, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         if (not 'bind_address' in data) or (not 'mask' in data):
#             msg = "Invalid Params".format(database_id)
#             return log_and_response(msg=msg, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         bind_address = data['bind_address']
#         mask = data['mask']

#         try:
#             DatabaseBind.objects.get(database= database, bind_address= bind_address + '/' + mask)
#         except Exception, e:
#             msg = "Bind {} does not exist.".format(bind_address)
#             return log_and_response(msg=msg, e=e, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         task = bind_address_on_database.delay(database, bind_address, mask, action="deny", user=user)

#         return Response(get_task_url(task.id),status.HTTP_204_NO_CONTENT)



# def log_and_response(msg, http_status, e="Conditional Error."):
#     LOG.warn(msg)
#     LOG.warn("Error: {}".format(e))

#     return Response(msg, http_status)

# def get_task_url(task_id):
#     return  {"task": Site.objects.get_current().domain + '/api/task?task_id=%s' %  str(task_id)}
