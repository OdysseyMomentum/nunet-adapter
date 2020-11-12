import unittest
import random
import string
import bcrypt
import secrets
from sqlalchemy.orm import scoped_session, sessionmaker
import logging
from db import ConsumerCredential,  ConsumerDevice , ProviderDevice ,Subprocess , RewardTable
from db.interface import Database
from sqlalchemy import create_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import admin
import time
class TestSessionManager(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        admin.set_db()
        self.email="admin@admin.com"
        self.password="test"
        self.device_name="samsung"
        self.providername="test"
        self.providerpassword="test"
        self.providerdevice="techno"
        self.reward=20
        self.dog_breed="bulldog"
        self.breed_image="dog.jpg"
        self.stub=admin.get_session_manager_stub()

    def test_a_add_credential(self):
        #before adding credential
        test_1=self.db.query(ConsumerCredential,email=self.email)
        self.assertIsNone(test_1)
        #after adding credential
        admin.add_credential(self.email, self.password)
        test_1=self.db.query(ConsumerCredential,email=self.email)
        self.assertIsNotNone(test_1)
        self.assertEqual(test_1.email,self.email)

    def test_b_add_device(self):
        
        #before adding device
        test_1=self.db.query(ConsumerDevice,email=self.email)
        self.assertIsNone(test_1)
        #after adding device
        admin.add_device(self.email, self.password,self.device_name)
        test_1=self.db.query(ConsumerDevice,email=self.email)
        self.assertIsNotNone(test_1.device_name)
        self.assertEqual(test_1.device_name,self.device_name)

    def test_c_activate_device(self):
        admin.activate_device(self.email,self.password,self.device_name)
        test_1=self.db.query(ConsumerCredential,email=self.email,active_device=self.device_name)
        self.assertEqual(test_1.active_device,self.device_name)


    def test_d_add_providerdevice(self):
        #before adding
        test_1 = self.db.query(ProviderDevice,memory_limit=1.1)
        self.assertIsNone(test_1)
        #after adding
        admin.add_provider_device(device_name=self.providerdevice,memory_limit=1.1, net_limit=1.1, cpu_limit=1.1
                        ,up_time_limit=1.1 , cpu_price=1.1, ram_price=1.1, net_price=1.1)

       
       
        test_1 = self.db.query(ProviderDevice,memory_limit=1.1)
        self.assertEqual(test_1.device_name,self.providerdevice)

    def test_e_add_dog_breeds(self):
        #before adding
        self.db.delete(RewardTable, breed_image = self.breed_image)
        test_1 = self.db.query(RewardTable, breed_image=self.breed_image,reward=self.reward)
        self.assertIsNone(test_1)
        #after adding
        admin.add_dog_breeds(self.dog_breed,self.breed_image,self.reward)
        test_1 = self.db.query(RewardTable, breed_image=self.breed_image,reward=self.reward)
        self.assertIsNotNone(test_1)
        self.assertEqual(test_1.breed_name,self.dog_breed)

    def test_f_delete_one_credential(self):
        #before adding credential
        new_email="admin2@admin.com"
        test_1=self.db.query(ConsumerCredential,email=new_email)
        self.assertIsNone(test_1)
        #after adding credential
        admin.add_credential(new_email, self.password)
        test_1=self.db.query(ConsumerCredential,email=new_email)
        self.assertIsNotNone(test_1)
        self.assertEqual(test_1.email,new_email)
        #after deleting credential
        admin.delete_one_credential(new_email)
        test_1=self.db.query(ConsumerCredential,email=new_email)
        self.assertIsNone(test_1)

    def test_g_admin_credential(self):
        admin.delete_all_credentials()
        #before adding credential
        test_1=self.db.query_all(ConsumerCredential,email=self.email)
        self.assertEqual([],test_1)
        #adding credential
        admin.add_credential(self.email, self.password)
        test_1=self.db.query(ConsumerCredential,email=self.email)
        self.assertEqual(test_1.email,self.email)
        #after deleting credential
        admin.delete_all_credentials()
        test_1=self.db.query(ConsumerCredential,email=self.email)
        self.assertIsNone(test_1)

    def test_e2_delete_device(self):
       #after deletion
        admin.delete_device(self.email,self.password,self.device_name)
        test_1=self.db.query(ConsumerDevice,email=self.email)
        self.assertIsNone(test_1)



if __name__ == '__main__':
   unittest.main()
