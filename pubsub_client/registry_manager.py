import time, pathlib, sys, datetime, threading, json

from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
from enum import Enum, IntEnum

project_dir = str(pathlib.Path(__file__).resolve().parents[0])
sys.path.append(project_dir)

from logger import getLogger
from utils import try_except
from rabbitmq_service import PikaPubSub

logger = getLogger(__file__)

class ModuleRegistry(BaseModel):
    module: str
    tool: str
    is_running:bool
    last_seen: str
    status: Optional[str]
    


class RegistryManager():
    def __init__(self) -> None:
        self.channel = "/tasks/registry"
        self.module_registry = {}
        self.isListening = False
    
    def register_module(self, module:str, tool:str,is_running:bool,status="ok" ):

        self.pika_pub_sub = PikaPubSub(queue_name=self.channel)
        message = ModuleRegistry(module=module, tool=tool, last_seen=datetime.datetime.now().isoformat(), is_running=is_running, status=status)
        self.pika_pub_sub.publish(message=message.dict())
    
    def get_available_modules(self):
        return self.module_registry

    def check_if_module_is_registered(self, module_name) -> bool:
        return True if module_name in self.module_registry.keys() else False

    def get_module_data(self, module_name) -> ModuleRegistry:
        return self.module_registry.get(module_name)
    
    def listen_for_modules(self):
        self.isListening = True
        listener = threading.Thread(target=self.__listen_handler, args=())
        listener.start()

    def __listen_handler(self):
        self.pika_pub_sub = PikaPubSub(queue_name=self.channel)
        try:
            while self.isListening:
                logger.info(f"Waiting for  {self.channel}")
                self.pika_pub_sub.subscribe(self.__update_module_registry)
                time.sleep(0.5)
        except BaseException:
            logger.exception("from Registry Manager")
            sys.exit(1)
    
    def __update_module_registry(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

        if body is not None: 
            message = json.loads(body)
            module_data = ModuleRegistry.parse_obj(message)
            self.module_registry.update(
                {
                    module_data.module+'/'+module_data.tool: module_data
                }
            )

    def close(self):
        self.isListening = False
        


    