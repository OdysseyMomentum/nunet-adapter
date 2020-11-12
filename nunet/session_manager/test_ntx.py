import unittest
from ntx import *

class TestNtx(unittest.TestCase):
    def setUp(self):
        self.public_key_creater = "0xFc27a434EfcF8BF4b6c7D4f69387f3d2Ee4d814e"
        self.value=1
        self.public_key_reciever="0xb5114121A51c6FfA04dBC73F26eDb7B6bfE2eB35"
        self.ntx=ntx()

    def test_mine(self):
        balance1=self.ntx.get_balance(self.public_key_creater)
        self.ntx.mine(self.value)
        balance2=self.ntx.get_balance(self.public_key_creater)
        balance1+=self.value
        self.assertEqual(balance1,balance2)

    def test_transfer(self):
        balance1=self.ntx.get_balance(self.public_key_reciever)
        self.ntx.mine(self.value)
        self.ntx.transfer(self.value,self.public_key_reciever)
        balance2=self.ntx.get_balance(self.public_key_reciever)
        balance1+=self.value
        self.assertEqual(balance1,balance2)


if __name__ == '__main__':
   unittest.main()

