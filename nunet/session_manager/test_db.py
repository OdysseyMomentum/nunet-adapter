import unittest
import random
import string
import bcrypt
import secrets
from sqlalchemy.orm import scoped_session, sessionmaker
import logging
from db import ConsumerCredential, ConsumerDevice
from db.interface import Database
from sqlalchemy import create_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


class TestSessionManager(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.email="testdb@test.com"
        self.password="test"
        self.device_name="samsung"
    def test_create(self):
    #ConsumerCredential
        #should save ConsumerCredential
        self.db.add(ConsumerCredential, email=self.email, password=self.db.hash_password(self.password))
        test_1=self.db.query(ConsumerCredential,email=self.email)
        print(test_1.email)
        self.assertIsNotNone(test_1)
        self.assertEqual(test_1.email,self.email)
       #should not save again
        self.db.add(ConsumerCredential, email=self.email, password=self.db.hash_password(self.password))
        test_1=self.db.query_all(ConsumerCredential,email=self.email)
        self.assertEqual(len(test_1),1)

    def test_hashpassword(self):
        expected=bcrypt.hashpw(self.password.encode('utf-8'),bcrypt.gensalt())
        self.assertIsNotNone(self.db.hash_password(self.password))
        self.assertEqual(len(expected),len(self.db.hash_password(self.password)))

    def test_checkpassword(self):
        self.assertTrue(self.db.check_password(self.password,self.db.hash_password(self.password)))
        self.assertFalse(self.db.check_password("@1efakepassword",self.db.hash_password(self.password)))

    def test_query(self):
        lattest_email="testdb2@test.com"
        lattest_password="test2"
        self.db.add(ConsumerCredential, email=lattest_email, password=self.db.hash_password(lattest_password))
        test_1=self.db.query(ConsumerCredential,email=lattest_email)
        self.assertEqual(test_1.email,lattest_email)
        self.assertNotEqual(test_1.email,self.email)

        test_1=self.db.query(ConsumerCredential,email=lattest_email, password=lattest_password)
        self.assertEqual(test_1.email,lattest_email)

        test_1=self.db.query(ConsumerCredential,email="fakeemail@test.com",password=lattest_password)
        self.assertIsNone(test_1)

    def test_update(self):
        self.db.add(ConsumerDevice,device_name=self.device_name,access_token=secrets.token_urlsafe(),email=self.email)
        before_update_tkn=self.db.query(ConsumerDevice,device_name=self.device_name,email=self.email).access_token

        devices = self.db.query_all(ConsumerDevice, email=self.email)
        self.assertEqual(devices[0].email, self.email)
        access_token=secrets.token_urlsafe()
        self.db.update(ConsumerDevice,
                           where={"email": self.email,
                                  },
                           update={"access_token": access_token})
        after_update_tkn=Database().query(ConsumerDevice,device_name=self.device_name,email=self.email).access_token

        self.assertNotEqual(before_update_tkn,after_update_tkn)

    def test_delete(self):
        self.db.add(ConsumerDevice,device_name="device2",access_token=secrets.token_urlsafe(),email=self.email)
        before_delete=self.db.query(ConsumerDevice,device_name="device2",email=self.email)
        self.db.delete(ConsumerDevice, device_name = "device2",email=self.email)
        after_delete=self.db.query(ConsumerDevice,device_name="device2",email=self.email)
        self.assertNotEqual(before_delete,after_delete)

    def drop(self):
        self.db.drop

if __name__ == '__main__':
   unittest.main()
