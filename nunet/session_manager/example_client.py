import logging
import grpc
import session_manager_client as sm
from datetime import datetime
import json
import os

class Session:

    def __init__(self):
        self.stub = sm.get_stub()
        self.container = "uclnlp"
        self.img=["artifacts/image1/img1.jpg","artifacts/image1/img2.jpg","artifacts/image1/img3.jpg","artifacts/image1/img4.jpg","artifacts/image1/img5.jpg","artifacts/image1/img6.jpg","artifacts/image1/img7.jpg","artifacts/image1/img8.jpg","artifacts/image1/img9.jpg","artifacts/image1/img10.jpg"]

    def signup(self):
        try:
             sm.signup(self.stub, self.email, self.password)
        except:
             logging.info("You have already registered")
    
    def uclnlp(self):
        sm.StartStats(self.stub, self.container)
    
    def stopuclnlp(self):
        sm.StopStats(self.stub, self.container)

if __name__ == '__main__':
   sess=Session()
   sess.uclnlp()
