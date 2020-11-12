import grpc
import logging

from session_manager_server import (sm_pb2_grpc,
                                    sm_pb2)
import secrets

from db import ConsumerCredential,  ConsumerDevice, Tasks , TaskExecutions ,  ProviderDevice ,Subprocess , RewardTable
from db.interface import Database



opencog_services = None
named_entity_server = None
sentiment_analysis_server = None

log = logging.getLogger("session_manager_admin")

db = None

def set_db(logger=None):
    global db
    db = Database(logger)


def show_credentials():
    db.print_table(ConsumerCredential)


def show_services():
    db.print_table(Service)


def show_devices():
    db.print_table(ConsumerDevice)


def add_credential(email,  password):
    if db.add(ConsumerCredential,email=email, password=db.hash_password(password)):
        log.info("Credential with email '{}' added.".format(email))
    else:
        log.error("Error adding '{}'!".format(email))


def add_device(email, password, device_name):
    cred = db.query(ConsumerCredential,
                    email=email,
                    password=password)
    device = db.query(ConsumerDevice,
                      email=email,
                      device_name=device_name)
    if cred and not device:
        if db.add(ConsumerDevice,
                  email=email,
                  device_name=device_name):
            log.info("Device '{}' added to User '{}'.".format(device_name,
                                                              email))
    else:
        log.error("Error adding device '{}'!".format(device_name))


def activate_device(email, password, device_name):
    cred = db.query(ConsumerCredential,
                    email=email,
                    password=password)
    device = db.query(ConsumerDevice,
                      email=email,
                      device_name=device_name)
    if cred and device:
        db.update(ConsumerCredential,
                  where={"email": email},
                  update={"active_device": device_name})
        log.info("Device '{}' is active".format(device_name))
    else:
        log.error("Error activating device '{}'!".format(device_name))




def add_provider_device(device_name, memory_limit, net_limit, cpu_limit
                        ,up_time_limit , cpu_price, ram_price, net_price):
   
   
    if db.add(ProviderDevice,
                  device_name=device_name,
                  memory_limit=memory_limit,
                  net_limit=net_limit,
                  cpu_price=cpu_price,
                  ram_price= ram_price,
                  net_price=net_price,
                  cpu_limit = cpu_limit,
                  up_time_limit = up_time_limit):
        log.info("Device  added ...")



    else:
        log.error("Error adding device !")

def add_dog_breeds(breed_name, breed_image, reward):
    if db.add(RewardTable, breed_name=breed_name, breed_image=breed_image,reward=reward):
        log.info("Dog breed '{}' is  added.".format(breed_name))
    else:
        log.error("Error adding '{}'!".format(breed_name))



def delete_provider_device(device_name):
    pdevice = db.query(ProviderDevice,
                        device_name = device_name)

    if pdevice:
        if db.delete(ProviderDevice, device_name=device_name):
            log.info("Provider Device '{}' deleted.".format(device_name))
            return
    log.error("Error deleting provider  device '{}'!".format(device_name))


def delete_one_credential(email):
    if db.delete(ConsumerCredential, email=email):
        log.info("User '{}' deleted.".format(email))
    else:
        log.error("Error deleting user '{}'!".format(email))


def delete_all_credentials():
    all_entries = db.query_all(ConsumerCredential)
    for c in all_entries:
        db.delete(ConsumerCredential, email=c.email)


def delete_device(email, password, device_name):
    cred = db.query(ConsumerCredential,
                    email=email,
                    password=password)
    device = db.query(ConsumerDevice,
                      email=email,
                      device_name=device_name)
    if cred and device:
        if db.delete(ConsumerDevice, dev_id=device.dev_id):
            log.info("Device '{}' deleted.".format(device_name))
            return
    log.error("Error deleting device '{}'!".format(device_name))


def login(email, password, device_name):
    stub = get_session_manager_stub()
    status, access_token = grpc_login(stub, email, password, device_name)
    log.info("Login [{}], Status: {}".format(access_token, status))


def logout(access_token, device_name):
    stub = get_session_manager_stub()
    status = grpc_logout(stub, device_name, access_token)
    log.info("Logout [{}], Status: {}".format(access_token, status))



def get_session_manager_stub(host="localhost", port=50000):
    channel = grpc.insecure_channel("{}:{}".format(host, port))
    return sm_pb2_grpc.SessionManagerStub(channel)


def grpc_login(stub, email, password, device_name):
    try:
        r = stub.login(sm_pb2.LoginInput(email=email,
                                         password=password,
                                         device_name=device_name))
        return r.status, r.access_token
    except Exception as e:
        log.error(e)
        return 1, ""


def grpc_logout(stub, access_token, device_name):
    try:
        r, _ = stub.logout.with_call(sm_pb2.LogoutInput(
            device_name=device_name), metadata=(("access_token", access_token),))
        return r.status
    except Exception as e:
        log.error(e)
        return "Fail"
