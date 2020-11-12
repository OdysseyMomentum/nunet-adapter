import json
import grpc
import sys
import os
import logging
import argparse
import random
import string
import time as t
import json
import urllib3
import secrets
from concurrent import futures
import datetime
from db import ConsumerCredential, TaskExecutions, ConsumerDevice , Tasks, Execution ,Subprocess , RewardTable , ProviderDevice
from db.interface import Database
from fractions import Fraction
from sqlalchemy.ext.declarative import DeclarativeMeta
import base64
import data_manager as dm
import pickle
import session_pb2_grpc as sm_pb2_grpc
import session_pb2 as sm_pb2
from google.protobuf import empty_pb2
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from organizer import Orchestrator
from constants import MAX_LOAD


logging.basicConfig(format="%(asctime)s - [%(levelname)8s] "
                           "- %(name)s - %(message)s", level=logging.INFO)
log = logging.getLogger("session_manager")

ONE_DAY_IN_SECONDS = 60 * 60 * 24

YOLO_PROVIDER_TOKEN_PER_TASK = 2 #TODO it's static value for now, needs to be calculated here

CNTK_PROVIDER_TOKEN_PER_TASK = 13 #TODO it's static value for now, needs to be calculated here

# nunet port
nunet_port = 50000

class Status:
    OK = 0
    UNAUTHENTICATED = 1
    CANCELLED = 2
    UNKNOWN = 3
    NO_Sufficient_TOKEN =4

class Tag:
    ERROR = "error"
    LOG = "log"
    UCLNLP_STAT = "uclnlp_stat"
    ATHENE_STAT = "athene_stat"
    NEWS_SCORE_STAT = "news_score_stat"

    UCLNLP_PROVIDER = "uclnlp"
    ATHENE_PROVIDER = "athene"
    NEWS_SCORE_PROVIDER = "news_score"

    UCLNLP_PUBK="0xb5114121A51c6FfA04dBC73F26eDb7B6bfE2eB35"
    ATHENE_PUBK="0xb5114121A51c6FfA04dBC73F26eDb7B6bfE2eB35"
    NEWS_SCORE_PUBK="0xb5114121A51c6FfA04dBC73F26eDb7B6bfE2eB35"


class SessionManagerServicer(sm_pb2_grpc.SessionManagerServicer):

    def __init__(self, db_session,  timeout=20):
        self.db = db_session
        self.timeout = timeout
        self.min_token = 20
        self.token_spent_yolo_process = 2
        self.token_spent_cntk_process = 13
        self.top_5=''
        self.exec_num=0
        self.exited_num=0
        self.queue_call=[]
        self.orc = Orchestrator()
        



    def execute(self, request, context):
        self.exec_num+=1
        net_exec=self.exec_num-self.exited_num
        print("total number of executing calls:",str(self.exec_num-self.exited_num))
        if net_exec<MAX_LOAD:
            cred, device, access_token  = self.validate_access(context)
            if not access_token:
                return self.set_grpc_context(context, sm_pb2.ExecutionOutput(), "Invalid access!", grpc.StatusCode.UNAUTHENTICATED)


            if self.min_token  > cred.token:
                return self.set_grpc_context(context, sm_pb2.ExecutionOutput(), "there is no sufficient token", grpc.StatusCode.NO_Sufficient_TOKEN)

            im_data = base64.b64decode(request.base64)
            time = datetime.datetime.now()
            filename = "imdata/{0}_input_im_{1}.jpg".format(cred.email, time)
            with open(filename, 'wb') as f:
                f.write(im_data)
            orc = Orchestrator()

            orc=orc.call(request.base64,cred.email)
        
        else:
            self.queue_call.append(context)
            cnt=0
            while True:
                t.sleep(2)
                if cnt==0:
                    print(str(self.exec_num-self.exited_num),"execution are on process.")
                    yield sm_pb2.ExecutionOutput(log_info = "All devices on NuNet platform are currently busy. Your request is scheduled for execution when a resource becomes available. Please wait for a notification.", tag = Tag.ON_QUEUE)
                    cnt+=1
                if self.exec_num-self.exited_num-len(self.queue_call)<MAX_LOAD:
                    yield sm_pb2.ExecutionOutput(log_info = "Your task is currently executing", tag = Tag.ON_QUEUE)
                    context=self.queue_call.pop(0)
                    cred, device, access_token  = self.validate_access(context)
                    if not access_token:
                        return self.set_grpc_context(context, sm_pb2.ExecutionOutput(), "Invalid access!", grpc.StatusCode.UNAUTHENTICATED)


                    if self.min_token  > cred.token:
                        return self.set_grpc_context(context, sm_pb2.ExecutionOutput(), "there is no sufficient token", grpc.StatusCode.NO_Sufficient_TOKEN)

                    im_data = base64.b64decode(request.base64)
                    time = datetime.datetime.now()
                    filename = "imdata/{0}_input_im_{1}.jpg".format(cred.email, time)
                    with open(filename, 'wb') as f:
                        f.write(im_data)
                    orc = Orchestrator()

                    orc=orc.call(request.base64,cred.email)                
                
                    break

        for tag, lg , breed in orc:
            reward = self.db.query(RewardTable, breed_name = breed)
            if tag==Tag.YOLO_RESULT:
                #dm.updateToken(self.db, cred, 10 )
                yolo_execution_id , task_id= dm.addTask(self.db, cred ,  lg ,Tag.YOLO_SUB_ID)
                yield sm_pb2.ExecutionOutput(log_info = lg, tag= tag)
                yield sm_pb2.ExecutionOutput(log_info = str(task_id), tag= Tag.TASK_ID)

            elif tag==Tag.BAD_RESULT:
                self.exited_num+=1
                print("process exited with bad result at the yolo stage. Current number of execution:",str(self.exec_num-self.exited_num))
                dm.updateToken(self.db , cred, -self.token_spent_yolo_process)
                yolo_execution_id , task_id= dm.addTask(self.db, cred , lg , Tag.YOLO_SUB_ID)
                yield sm_pb2.ExecutionOutput(log_info = lg, tag= tag)
                yield sm_pb2.ExecutionOutput(log_info = str(task_id), tag= Tag.TASK_ID)
            elif tag==Tag.ERROR:
                self.exited_num+=1
                print("process exited with error at the yolo stage. Current number of execution:",str(self.exec_num-self.exited_num))
                yolo_execution_id, task_id  = dm.addTask(self.db, cred ,  lg, Tag.YOLO_SUB_ID )
                yield sm_pb2.ExecutionOutput(log_info = lg, tag = tag)
                yield sm_pb2.ExecutionOutput(log_info = str(task_id), tag= Tag.TASK_ID)
            elif tag==Tag.CNTK_ERROR:
                self.exited_num+=1
                print("process exited with error at the cntk stage. current number of execution:",str(self.exec_num-self.exited_num))
                cntk_execution_id = dm.addExecution(self.db , lg, Tag.CNTK_SUB_ID , task_id )
                yield sm_pb2.ExecutionOutput(log_info = lg, tag = tag)
            elif tag==Tag.DOG_IM:
                print("dog im")
            elif tag==Tag.SAVE_OUTPUT:
                self.db.update(Execution, where = { "execution_id" : yolo_execution_id},
                                          update ={"image_output" : lg}  )

            elif tag==Tag.CNTK_RESULT:
                self.exited_num+=1
                if not reward:
                    reward = 20
                else:
                    reward = reward.reward
                cntk_execution_id = dm.addExecution(self.db, lg, Tag.CNTK_SUB_ID , task_id  )
                self.db.update(Tasks, where={"task_id": task_id},
                                      update={"reward": reward })
                dm.updateToken(self.db , cred, reward - (self.token_spent_cntk_process + self.token_spent_yolo_process))
                yield sm_pb2.ExecutionOutput(log_info = lg, tag= tag)

            elif tag==Tag.YOLO_OUTPUT:

                yield sm_pb2.ExecutionOutput(log_info = lg,  tag= tag)

            elif tag==Tag.TOP_5:
                self.db.update(Execution, where={"execution_id": cntk_execution_id},
                                          update={"json_result": lg })

            elif tag==Tag.YOLO_STAT or tag==Tag.CNTK_STAT:
                log.info("Registering new subprocess:")
                if tag==Tag.YOLO_STAT:
                    dm.updateExecution(self.db, yolo_execution_id, lg, YOLO_PROVIDER_TOKEN_PER_TASK, filename)
                    dm.updateProviderDeviceData(self.db,Tag.YOLO_PROVIDER, lg)
                else:
                    dm.updateExecution(self.db, cntk_execution_id, lg, CNTK_PROVIDER_TOKEN_PER_TASK)
                    dm.updateProviderDeviceData(self.db,Tag.CNTK_PROVIDER, lg)
                stat= json.dumps(lg)
                yield sm_pb2.ExecutionOutput(log_info =stat, tag= tag)

            else:
                yield sm_pb2.ExecutionOutput(log_info = lg,tag= tag)




    def provider(self, request, context):
        cred, _, access_token = self.validate_access(context)
        if not access_token:
            return self.set_grpc_context(context,
                                         sm_pb2.PreviousTasksOutput(),
                                         "Invalid access!",
                                         grpc.StatusCode.UNAUTHENTICATED)

        devices = self.db.query_all(ProviderDevice)
        response= sm_pb2.ProviderOutput()
        for dev in devices:
            response.device.add(device_name = dev.device_name,
                                process_completed=dev.process_completed,
                                token_earned= dev.token_earned )


        return  response


    def providerDevice(self, request, context):
        cred, _, access_token = self.validate_access(context)
        if not access_token:
            return self.set_grpc_context(context,
                                         sm_pb2.UserInfoOutput(),
                                         "Invalid access!",
                                         grpc.StatusCode.UNAUTHENTICATED)
        device = self.db.query(ProviderDevice , device_name = request.device_name )

        return sm_pb2.ProviderDeviceOutput(cpu_limit=device.cpu_limit,
                                      cpu_used = device.cpu_used,
                                      memory_limit = device.memory_limit,
                                      memory_used = device.memory_used,
                                      net_limit = device.net_limit,
                                      net_used = device.net_used,
                                      max_up_time= device.up_time_limit,
                                      used_up_time= device.up_time_used,
                                      cpu_price = device.cpu_price,
                                      ram_price = device.ram_price,
                                      net_price = device.net_price

                                      )



    def telemetry(self, request, context):
        cpu_used = request.cpu_used
        memory_used = request.memory_used
        time_taken = request.time_taken
        net_used = request.net_used
        device_name=request.device_name
        if device_name=="uclnlp":
            pubk=Tag.UCLNLP_PUBK
        if device_name=="athene":
            pubk=Tag.ATHENE_PUBK
        if device_name=="news_score":
            pubk=Tag.NEWS_SCORE_PUBK
        stat = {
           "time_taken": time_taken,
           "total_memory": memory_used, # is not memory percentage
           "net_rx": net_used,
           "cpu_usage":cpu_used# is not cpu percentage
          }
        txn=dm.updateProviderDeviceData(self.db,device_name, stat,pubk)
        
        return sm_pb2.TelemetryOutput(txn=str(txn))
    @staticmethod
    def set_grpc_context(context, message_type, msg, code=None):
        log.warning(msg)
        context.set_details(msg)
        if code:
            context.set_code(code)
        return message_type
    # Checks if the incoming request is valid

    @staticmethod
    def get_access_token(metadata):
        for key, value in metadata:
            if key == "access_token" and value:
                return value
        return None
    @staticmethod
    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}



class SessionManagerServer:
    def __init__(self,
                 port=nunet_port,
                ):


        self.db = Database()
        self.port = port
        self.server = None
        self.timeout = 30
    def start_server(self):
        hundred_MB = (1024 ** 2) * 100   # max grpc message size

        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=20),
            options=[
            ('grpc.max_receive_message_length', hundred_MB)
        ])

        sm_pb2_grpc.add_SessionManagerServicer_to_server(
            SessionManagerServicer(db_session=self.db,
                                   timeout=self.timeout), self.server )
        self.server.add_insecure_port("[::]:{}".format(self.port))
        log.info("Starting SessionManagerServer at localhost:{}".format(
            self.port))
        self.server.start()

    def stop_server(self):
        self.server.stop(0)





if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--port",
                        "-p",
                        type=int,
                        default=nunet_port,
                        help="Session manager server port")

    args = parser.parse_args()

    server = SessionManagerServer(
                                     port=args.port

                                  )
    server.start_server()

    try:
        while True:
            t.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop_server()
