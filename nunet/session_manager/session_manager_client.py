from __future__ import print_function
import logging

import grpc
import pickle
import numpy as np
import base64
import json
import session_pb2_grpc as sm_pb2_grpc
import session_pb2 as sm_pb2
import os



def Execute(stub,access_token, img):
    with open(img, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        img_path = encoded_string

    features= stub.execute(sm_pb2.ExecutionInput(base64 = img_path   ) ,
                                        metadata=(("access_token", access_token),))
    
    for feature in features:
        if feature.tag != "yolo_output":
            print("tag: {tag} log {log} ".format(tag = feature.tag, log=feature.log_info))
            if feature.tag=="yolo_stat":
                yolo_stat=feature.log_info
            if feature.tag=="cntk_stat":
                cntk_stat=feature.log_info
        else:
            im_data= base64.b64decode(feature.log_info)
            filename = 'nebaa.jpg'
            with open(filename, 'wb') as f:
                f.write(im_data)
    return yolo_stat,cntk_stat


def provider(stub, access_token):
    r,some= stub.provider.with_call(sm_pb2.Empty() ,
                                        metadata=(("access_token", access_token),))

    #print(r)
    #return print(type(r))
    return r
def processInfo(stub, access_token , task_id ):
    r,some= stub.processInfo.with_call(sm_pb2.ProcessInfoInput( task_id = task_id ) ,
                                        metadata=(("access_token", access_token),))


    # final_data = json.dumps(r)

    print(r)
    return print(type(r))


def providerDevice(stub, access_token , device_name):
    r,some= stub.providerDevice.with_call(sm_pb2.ProviderDeviceInput(device_name = device_name) ,
                                        metadata=(("access_token", access_token),))


    print(r)
    return print(type(r))



def telemetry(stub, cpu_used,memory_used,net_used,time_taken,device_name):
    response=stub.telemetry(sm_pb2.TelemetryInput(cpu_used=cpu_used,memory_used=memory_used,net_used=net_used,time_taken=time_taken,device_name=device_name))
    return response



def get_stub():
    try:
        nunet_port = os.environ['NUNET_PORT']
    except:
        nunet_port = None
        print("no env variable NUNET_PORT")
    if not nunet_port:
        nunet_port = 50000

    port = "localhost:" + str(nunet_port)
    channel = grpc.insecure_channel(port)
    stub = sm_pb2_grpc.SessionManagerStub(channel)

    return stub

if __name__ == '__main__':
    logging.basicConfig()
