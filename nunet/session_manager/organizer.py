import docker
import grpc
import os
import base64

import logging
import random
import datetime
import time
import json
import ast
import io
from io import BytesIO
import requests
import numpy as np
from io import BytesIO
import multiprocessing
from multiprocessing import Process,current_process
from random import randint
# name of nunet container
from constants import CONTAINER_NAME
class Tag:
    ERROR = "error"
    LOG = "log"
    UCLNLP_STAT = "uclnlp_stat"
    ATHENE_STAT = "athene_stat"
    NEWS_SCORE_STAT = "news_score_stat"
class Orchestrator:
    def __init__(self):
        self.client = docker.from_env(timeout=10000)
        self.dapi = docker.APIClient()
        self.uclnp=False
        self.athene=False
        self.news_score=False
        self.read_stats=True

    def cont_stat(self, log,cont,time_taken):
       logs=log
       previousCPU = logs['precpu_stats']['cpu_usage']['total_usage']
       cpuDelta = logs['cpu_stats']['cpu_usage']['total_usage'] - previousCPU #calculate the change for the cpu usage of the container in between readings
       previousSystem = logs['precpu_stats']['system_cpu_usage']
       systemDelta = logs['cpu_stats']['system_cpu_usage'] - previousSystem
       cpu_percent = 0
       if systemDelta > 0.0 and cpuDelta > 0.0:
           #calculate the change for the entire system between readings
           cpu_percent = ((cpuDelta / systemDelta) * len(logs['cpu_stats']['cpu_usage']['percpu_usage']) * 100) / multiprocessing.cpu_count()
           logging.info("CPU percentage of {container} :{0:.2f}%".format(cpu_percent,container=cont.image))
       else:
           logging.info("CPU percentage: "+ cpu_percent)
       memory_usage=(logs['memory_stats']['usage'])/10**6 #converting to MiB
       memory_limit=(logs['memory_stats']['limit'])/10**9 #converting to GiB
       memory_perc=memory_usage*100/(memory_limit*10**3)
       rx=logs['networks']['eth0']['rx_bytes']
       tx=logs['networks']['eth0']['tx_bytes']
       net_rx = rx/1024
       net_tx = tx/1024
       logging.info("Time Taken: {tm} seconds".format(tm=time_taken))
       logging.info("Memory Percentage: {mem_perc:.2f} %".format(mem_perc=memory_perc))
       logging.info("NET I/O: {rx} Kib / {tx}Kib".format(rx=rx/1024,tx=tx/1024))
       stat = {
           "memory_limit": memory_limit,
           "time_taken": time_taken,
           "memory_usage": memory_usage, # is not memory percentage
           "net_rx": net_rx,
           "net_tx": net_tx,
           "cpu_usage":((cpuDelta)/100)/10**6  # is not cpu percentage
       }
       return  stat
    def stream_stat_cont(self,cont,yolo_file):
        log=cont.stats(decode=True,stream=True)
        total_log=[]
        i=0
        for logs in log:
            total_log.append(logs)
        for log in total_log:
            try:
                if i>1:
                        res=self.cont_stat(log,cont,0)
                        if i==2:
                            with open(yolo_file+'.txt', 'a') as json_file:
                                json_file.write('{'+"'"+str(i)+"'"+":"+str(res))
                        else:
                            with open(yolo_file+'.txt', 'a') as json_file:
                                json_file.write(","+"'"+str(i)+"'"+":"+str(res))
            except:
                pass
            i+=1
    def get_resource_usage(self,res_file,delta_time):
        stat={
           "memory_limit": 0.0,
           "time_taken": 0.0,
           "memory_usage": 0.0, # is not memory percentage
           "net_rx": 0.0,
           "net_tx": 0.0,
           "cpu_usage":0.0,  # is not cpu percentage
           "total_memory":0.0
          }
        with open(res_file+'.txt', 'r') as reader:
            contents=reader.read()
        data=contents.replace("'",'"')+"}"
        cpu_total=0
        max_memory=0
        net_rx=0
        net_tx=0
        time_taken=0
        total_memory=0
        memory_limit=0
        try:
            json_data=json.loads(data)
        except:
            return stat
        index_mem=0
        for i in range(len(json_data)):
            if i>1:
                index=str(i)
                cpu_total+=json_data[index]['cpu_usage']
                if json_data[index]['memory_usage']>max_memory:
                    max_memory=json_data[index]['memory_usage']
                    index_mem=index
                total_memory+=json_data[index]['memory_usage']
        try:
            net_rx=json_data[index_mem]['net_rx']
            net_tx=json_data[index_mem]['net_tx']
            memory_limit=json_data[index_mem]['memory_limit']
            time_taken=json_data[index_mem]['time_taken']
        except:
            net_rx=0
            net_tx=0
            memory_limit=0
            net_tx
        stat = {
           "memory_limit": memory_limit,
           "time_taken": delta_time,
           "memory_usage": max_memory, # is not memory percentage
           "net_rx": net_rx,
           "net_tx": net_tx,
           "cpu_usage":cpu_total,  # is not cpu percentage
           "total_memory":total_memory
          }
        os.remove(res_file+".txt")
        return stat
    def start_get_res(self, container):
        net = self.client.networks.get(CONTAINER_NAME)
        if container=="uclnlp":
            stats_file="uclnlp"+str(int(time.time()))+str(randint(100,10000))
            open(stats_file+'.txt', 'w')
            self.uclnlp=True
        if container=="athene":
            stats_file="athene"+str(int(time.time()))+str(randint(100,10000))
            open(stats_file+'.txt', 'w')
            self.athene=True
        if container=="news_score":
            stats_file="news_score"+str(int(time.time()))+str(randint(100,10000))
            open(stats_file+'.txt', 'w')
            self.news_score=True
        #if stats_file:
        cont = self.client.containers.get(container)
        process1=Process(target=self.stream_stat_cont, args=(cont,stats_file,))
        process1.start()
        yield Tag.LOG, "Start getting resource", None
        get_resource = self.start_uclnlp_cont(cont, stats_file)
        for tag, log, res in get_resource:
            yield tag, log, res
    def start_uclnlp_cont(self, container,stats_file):
        stat=''
        start_time=time.time()
        hundred_MB = (1024 ** 2) * 100
        temp=self.read_stats
        while temp:
            temp=self.read_stats
            time.sleep(10)
        delta_time=float(format((time.time()-start_time),'.2f'))
        time.sleep(3)
        stat=self.get_resource_usage(stats_file,delta_time)
        yield Tag.UCLNLP_STAT, stat , None
    def stop_get_res(self, container):
        self.read_stats=False
