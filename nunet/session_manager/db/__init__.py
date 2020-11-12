from sqlalchemy import Column, Integer, String, ForeignKey ,Float ,DateTime , Boolean , Binary
from sqlalchemy.orm import relationship
import datetime
from .interface import Base


class ConsumerCredential(Base):
    __tablename__ = "consumercredential"
    email = Column(String(256),
                      primary_key=True,
                      unique=True,
                      nullable=False)
    password = Column(Binary(60))
    picture = Column(String())
    is_guest = Column(Boolean, default=False)
    token = Column(Float, default=50.00)
    tasks =relationship("Tasks",backref="consumercredential", single_parent=True)
    active_device = Column(String(256), default="")
    devices = relationship("ConsumerDevice",
                           backref="consumercredential",
                           lazy=True,
                           cascade="all, delete, delete-orphan",
                           single_parent=True)

    def __repr__(self):
        return "EMAIL     : {}\n" \
               "IS_GUEST     : {}\n" \
               "TOKEN        : {}\n" \
               "ACTIVE_DEVICE: {}\n" \
               "DEVICES      : {}\n".format(self.email,
                                            self.is_guest,
                                            self.token,
                                            self.active_device,
                                            self.devices)


class ConsumerDevice(Base):
    __tablename__ = "consumerdevices"
    dev_id = Column(Integer, primary_key=True)
    device_name = Column(String(256), nullable=False)
    access_token = Column(String(256), default="")
    email = Column(String(256),
                      ForeignKey("consumercredential.email"),
                      nullable=False)

    def __repr__(self):
        return "EMAIL    : {}\n" \
               "DEVICE_NAME : {}\n" \
               "ACCESS_TOKEN: {}\n".format(self.email,
                                           self.device_name,
                                           self.access_token)


class Tasks(Base):
    __tablename__="tasks"
    task_id = Column(Integer, primary_key= True)
    index = Column(Integer)
    date = Column(DateTime, default=datetime.datetime.now())
    tasks_executions =relationship("TaskExecutions",backref="tasks", single_parent=True)
    reward = Column (Float())
    share_token = Column(String(256),nullable=True, unique=True)
    email= Column(String(256),
                      ForeignKey("consumercredential.email"),
                      nullable=False)


class TaskExecutions(Base):
    __tablename__ ="taskexecutions"
    task_execution_id = Column(Integer, primary_key = True)
    order =Column(Integer)
    execution_id = Column(Integer)
    task_id= Column(Integer,
                      ForeignKey("tasks.task_id"),
                      nullable=False)


class Execution(Base):
    __tablename__ = "execution"
    execution_id = Column(Integer, primary_key=True)
    subprocess_id = Column(Integer,default= 0)
    input_image = Column(String(), default="")
    image_output = Column(String(), default="")
    date = Column(DateTime, default=datetime.datetime.now())
    cpu_usage = Column(Float(precision=4), default=0.0)
    time_taken = Column(Float(precision=4), default=0.0)
    memory_usage = Column(Float(precision=4), default = 0.0)
    time_of_run = Column(Float(precision=4), default = 0.0)
    token_earned = Column(Integer, default = 0)
    result = Column(String(), default="")
    network_tx = Column(Float(precision=4), default =0.0)
    network_rx = Column(Float(precision=4), default = 0.0)
    dev_id = Column(Integer)
    json_result = Column(String(), default="")
    total_memory = Column(Float(), default=0.0)



    def __repr__(self):
        return "NETWORK_TX: {}\n" \
                "DATE            : {}\n" \
               "NETWORK_RX: {}\n" \
               "CPU_PERCETAGE: {}\n".format(self.network_tx,
                                           self.network_rx,
                                           self.cpu_percetage,
                                           self.sub_process_name,
                                           self.date)


class Subprocess(Base):
    __tablename__ = "subprocess"
    subprocess_id = Column(Integer,primary_key=True)
    subprocess_name = Column(String(256), nullable=False)
    explanation = Column(String(256), default="")
    disk_io_requirement = Column(String())
    cpu_usage_requirement = Column(String())
    memory_usage_requirement =Column(String())

    def __repr__(self):
        return  "SUBPROCESS_NAME        : {}\n" \
                "DISK_IO_REQUIREMENT        : {}\n" \
               "EXPLANATION : {}\n" \
               "CPU_USAGE_REQUIREMENT : {}\n" .format(self.explanation,
                                               self.subprocess_name,
                                               self.disk_io_requirement,
                                               self.cpu_usage_requirement,
                                               self.memory_usage_requirement)


class ProviderDevice(Base):
    __tablename__ = "providerdevice"
    dev_id = Column(Integer, primary_key=True)
    device_name = Column(String(256),
                         nullable=False)
    process_completed = Column(Integer , default= 0 )
    token_earned = Column(Float, default = 0.0)
    memory_limit = Column(Float, default = 0.0)
    memory_used = Column(Float, default = 0.0)
    net_limit = Column(Float, default = 0.0)
    net_used = Column(Float, default = 0.0)
    cpu_limit = Column(Float, default = 0.0)
    cpu_used = Column(Float, default = 0.0)
    up_time_limit = Column(Float, default  = 0.0)
    up_time_used = Column(Float, default = 0.0)
    cpu_price = Column(Float, default = 0.0)
    ram_price = Column(Float , default =0.0)
    net_price = Column(Float, default = 0.0)




    def __repr__(self):
        return  "DEVICE_NAME : {}\n" \
                "PROCESS_COMPLETED : {}\n" \
               "TOKEN_EARNED: {}\n".format(self.process_completed,
                                           self.device_name,
                                           self.token_earned)

class RewardTable(Base):
    __tablename__ = "rewardtable"
    breed_name = Column(String(256),
                      primary_key=True,
                      unique=True,
                      nullable=False)
    breed_image = Column(String(), nullable=False)
    reward = Column(Integer, default=20)

    def __repr__(self):
        return "BREED_NAME     : {}\n" \
               "IMAGEPATH        : {}\n" \
               "REWARD   : {}\n" .format(self.breed_name,
                                            self.breed_image,
                                            self.reward
                                            )

class SystemInfo(Base):
    __tablename__="systeminfo"
    system_id = Column(Integer, primary_key=True)
    max_load =Column(Integer)
