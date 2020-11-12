import unittest
import logging
import base64
from db.interface import Database
from concurrent import futures
import grpc
from db import ConsumerCredential, ConsumerDevice, Execution, Subprocess
import session_pb2_grpc as sm_pb2_grpc
import session_pb2 as sm_pb2
import datetime
from session_manager_server import SessionManagerServicer, SessionManagerServer, Status, Tag
import urllib.request
import os
import shutil
class sampleclient:

      def signup(stub, email, password):
            response = stub.signup(sm_pb2.SignupInput(email=email,
                                                password=password
                                                ))
            return response


      def login(stub, email, password, device_name):
            response = stub.login(sm_pb2.LoginInput(email=email,
                                                password=password,
                                                device_name = device_name  ))

            return response.access_token 

      def logout(stub , device_name , access_token):

          r,_ = stub.logout.with_call(sm_pb2.LogoutInput(device_name = 'samsung'   ) ,
                                        metadata=(("access_token", access_token),))

      def Execute(stub,access_token, img):
            with open(img, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                img_path = encoded_string

            features= stub.execute(sm_pb2.ExecutionInput(base64 = img_path   ) ,
                                        metadata=(("access_token", access_token),))

            return features
    
      def previousTasks(stub, access_token , offset, size ):
            r,some= stub.previousTasks.with_call(sm_pb2.PreviousTasksInput( offset = offset , size = size  ) ,
                                        metadata=(("access_token", access_token),))
            return r

      def processInfo(stub, access_token , task_id ):
            r,some= stub.processInfo.with_call(sm_pb2.ProcessInfoInput( task_id = task_id ) ,
                                        metadata=(("access_token", access_token),))
            return r



      def updateUserToken(stub, access_token ):
            r,some= stub.updateUserToken.with_call(sm_pb2.Empty() ,
                                        metadata=(("access_token", access_token),))
            return r
      

class TestSessionManagerServer(unittest.TestCase):

    sms = None

    @classmethod
    def setUpClass(self):
        self.sms=SessionManagerServer(port=5001)
        self.sms.start_server()

    @classmethod
    def tearDownClass(self):
        self.sms = None

    def setUp(self):
        urllib.request.urlretrieve("https://www.statnews.com/wp-content/uploads/2019/08/AdobeStock_182445295-645x645.jpeg", "dog.jpg")
        self.channel = grpc.insecure_channel('localhost:5001')
        self.stub = sm_pb2_grpc.SessionManagerStub(self.channel)
        self.email="servertest@test.com"
        self.password="test342"
        self.device_name="samsungnew1"
        self.img = "dog.jpg"
        self.access_token= "0A"
        self.timeout =20
        self.min_token = 23
        self.db = Database()

    def test_a_signup(self):
        self.db.query(ConsumerCredential,email=self.email)
        with grpc.insecure_channel("localhost:{}".format(5001)) as channel:
            user_1 = sampleclient.signup(self.stub, self.email, self.password)
            cred = self.db.query(ConsumerCredential, email=self.email, password=self.password)
            self.assertIsNotNone(cred)
            self.assertEqual(cred.email, self.email)
            self.assertEqual(user_1.status, Status.OK)

    def test_b_login(self):
        device_1 = sampleclient.login(self.stub, self.email, self.password, self.device_name)
        self.assertIsNotNone(device_1)
        device = self.db.query(ConsumerDevice, email=self.email, device_name=self.device_name)
        self.assertEqual(self.device_name, device.device_name )

    def test_c_logout(self):
      #before logout
        device_1 = sampleclient.login(self.stub, self.email, self.password, self.device_name)
        login_1 = sampleclient.login(self.stub, self.email, self.password, self.device_name)
        self.assertEqual(login_1,device_1)
      #after logout
        sampleclient.logout(self.stub, self.device_name,device_1)
        login_1 = sampleclient.login(self.stub, self.email, self.password, self.device_name)
        self.assertNotEqual(login_1,self.access_token)
        self.db.delete(ConsumerCredential,email=self.email,password=self.password)



if __name__ == "__main__":
    sms=SessionManagerServer(port=5001)
    sms.start_server()
    unittest.main()
