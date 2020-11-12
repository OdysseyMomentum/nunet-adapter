from db import ConsumerCredential, TaskExecutions, ConsumerDevice , Tasks, Execution ,Subprocess , RewardTable , ProviderDevice
import logging
import datetime
import secrets
log = logging.getLogger("session_manager")
import math
from ntx import *

ntx=ntx()
NEWS_SCORE_PROVIDER_PRICE = 2
ATHENE_PROVIDER_PRICE = 13
UCLNLP_PROVIDER_PRICE = 2

def updateToken(db, cred, token):
    log.info("Token update to User '{}'.".format(cred.email))
    db.update(ConsumerCredential,
                where={"email": cred.email},
                update={"token": cred.token + token })


def addTask(db,  cred , lg,order):
    time = datetime.datetime.now()
    try:
        task = db.query_all(Tasks, email = cred.email).pop()
    except:
        task = None
    if not task:
        index = 1
    else:
        index = task.index + 1
    if db.add(Tasks, email= cred.email, date = time ,index = index, share_token=secrets.token_urlsafe()):
            log.info("new task is recorded for user  '{}' ...".format(cred.email))
    else:
        log.error("Error adding new record of user '{}' ".format(cred.email))
        return None
    task = db.query(Tasks, email=cred.email, date=time)
    yolo_execution_id = addExecution(db, lg, order , task.task_id)
    return yolo_execution_id  , task.task_id


def addExecution( db,  result , order, task_id ):
    time = datetime.datetime.now()
    if db.add(Execution, subprocess_id = order, result= result, date = time):
        log.info("add new execution of user ")
    else:
        log.error("Error adding new execution ")
    execution = db.query(Execution, subprocess_id=order, date=time)
    addTaskExecution(db , order , task_id, execution.execution_id)
    return execution.execution_id
def addTaskExecution(db, order, task_id, execution_id):
        if db.add(TaskExecutions,
                        order = order,
                        task_id = task_id,
                        execution_id = execution_id):
                        log.info("success on adding new task execution")

        else:
            log.error("error adding new task execution")

def updateExecution( db, execution_id, lg, token, input_image = ""):
    db.update(Execution,
                            where = { "execution_id" : execution_id},
                            update ={ "network_rx": lg.get("net_rx"),
                                        "network_tx": lg.get("net_tx"),
                                        "memory_usage": lg.get("memory_usage"),
                                        "time_taken": lg.get("time_taken"),
                                        "cpu_usage" : lg.get("cpu_usage"),
                                        "total_memory" : lg.get("total_memory"),
                                        "token_earned" : token,
                                        "input_image" : input_image
                                    })



def updateProviderDeviceData(db,device_name ,lg,pubk):
    provider_device = db.query(ProviderDevice, device_name=device_name)
    process_completed = provider_device.process_completed + 1
    cpu_used = provider_device.cpu_used + lg.get("cpu_usage")
    memory_used = provider_device.memory_used + lg.get("total_memory")
    up_time_used = provider_device.up_time_used + lg.get("time_taken")
    net_used = provider_device.net_used + lg.get("net_rx")
    cpu_cost_per_process = cpu_used * provider_device.cpu_price
    ram_cost_per_process = memory_used * provider_device.ram_price
    net_cost_per_process = net_used * provider_device.net_price
    cost_per_process = math.ceil(cpu_cost_per_process + ram_cost_per_process + net_cost_per_process)
    ntx.mine(cost_per_process)
    txn=ntx.transfer(cost_per_process,pubk)
    token_earned = provider_device.token_earned + cost_per_process

    db.update(ProviderDevice, where ={"device_name": device_name},
                                update ={"token_earned": token_earned,
                                         "cpu_used": cpu_used,
                                         "memory_used": memory_used,
                                         "up_time_used": up_time_used,
                                         "net_used": net_used,
                                         "process_completed": process_completed})
    return txn

def newExecution( db, order,lg,device_name):
    provider_device = db.query(ProviderDevice, device_name=device_name)
    cpu_used = lg.get("cpu_usage")
    memory_used = lg.get("total_memory")
    time_taken = lg.get("time_taken")
    net_used = lg.get("net_rx")
    cpu_cost_per_process = cpu_used * provider_device.cpu_price
    ram_cost_per_process = memory_used * provider_device.ram_price
    net_cost_per_process = net_used * provider_device.net_price
    cost_per_process = math.ceil(cpu_cost_per_process + ram_cost_per_process + net_cost_per_process)    
    time = datetime.datetime.now()
    result="Dog"
    if db.add(Execution, subprocess_id = order, result= result, date = time,cpu_usage=cpu_used,memory_usage=memory_used,time_taken=time_taken):
        log.info("add new execution of user ")
    else:
        log.error("Error adding new execution ")
    execution = db.query(Execution, subprocess_id=order, date=time)
    return execution.execution_id