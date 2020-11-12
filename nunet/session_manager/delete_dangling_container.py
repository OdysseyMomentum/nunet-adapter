import time
import datetime
import os
from multiprocessing import Process
import logging
import docker

class RemoveContainer:
    def __init__(self):
        self.sleep_time=360.0
        self.client=docker.from_env()
    def remove(self):
        print("running ...")
        while (True):
            yolo_containers_list=self.client.containers.list(all=True, filters={"ancestor":"yolov3-object-detection"})
            cntk_containers_list=self.client.containers.list(all=True, filters={"ancestor":"cntk-image-recon"})
            for yolo_cont in yolo_containers_list:
                try:
                    log=yolo_cont.logs(until=int(time.time()-self.sleep_time))
                except:
                    print("yolo cont removed")
                time.sleep(20.0)
                if "b''"!=str(log) or yolo_cont.status == "created":
                    try:
                        yolo_cont.remove(force=True)
                    except:
                        print("yolov-cont deleted manually")
                    print("dangling yolov-cont removed")

            for cntk_cont in cntk_containers_list:
                try:
                    log=cntk_cont.logs(until=int(time.time()-self.sleep_time))
                except:
                    print("cntk cont removed")
                time.sleep(20.0)
                if "b''"!=str(log) or cntk_cont.status == "created":
                    try:
                        cntk_cont.remove(force=True)
                    except:
                        print("cntk-cont deleted manually")
                    print("dangling cntk-cont removed")
            time.sleep(self.sleep_time)

    def start_remove(self):
            Process(target=self.remove,args=()).start()

if __name__ == "__main__":
    rc= RemoveContainer()
    rc.start_remove()
