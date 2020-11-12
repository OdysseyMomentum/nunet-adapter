import logging
import grpc
import session_manager_client as sm
from datetime import datetime
import json
import os

class Session:

    def __init__(self):
        self.stub = sm.get_stub()
        self.device_name = "uclnlp"
        self.cpu_used=1.0
        self.memory_used=1.0
        self.net_used=1.0
        self.time_taken=1.0

    
    def telemetry(self):
        response=sm.telemetry(self.stub, self.cpu_used,self.memory_used,self.net_used,self.time_taken,self.device_name)
        print(response)

if __name__ == '__main__':
   sess=Session()
   sess.telemetry()
