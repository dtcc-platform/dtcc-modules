#!/usr/bin/env python3

import os, pathlib, sys, datetime, time, re, asyncio, logging, json
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
import io
import uvicorn
from fastapi import FastAPI, Path, responses, status, Body, Query, BackgroundTasks, Response, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
from enum import Enum, IntEnum
from sse_starlette.sse import EventSourceResponse


logging.getLogger("pika").setLevel(logging.WARNING)


project_dir = str(pathlib.Path(__file__).resolve().parents[0])
sys.path.append(project_dir)

from pubsub_client.logger import getLogger
from pubsub_client.utils import try_except, DictStorage, file_exists
from pubsub_client.rabbitmq_service import PikaPubSub, log_consumer
from pubsub_client.registry_manager import RegistryManager
from pubsub_client.registry_manager import RegistryManager, ModuleRegistry

logger = getLogger(__file__)

pub_sub = PikaPubSub(queue_name="/task/run_sample_python_process")
pub_sub.publish(message={"cmd":"start"})

app = FastAPI(
    title="DTCC Core API",
    description="API for controlling modules",
    version="1.0"
)

registry_manager = RegistryManager()





def load_module_config():
    modules_config = {}
    modules_config_storage_path = os.path.join(project_dir,"dtcc-modules-conf.json")
    if file_exists(modules_config_storage_path):
        modules_config_storage = json.load(open(modules_config_storage_path,'r'))
    else:
        sys.exit(1)
        modules_config_storage = {}
    
    if len(modules_config_storage)>0:
        modules_list = modules_config_storage.get("modules")
        for module_info in modules_list:
            tool_info_list = module_info.get("tools")
            for tool_info in tool_info_list:
                modules_config[f"{module_info['name']}/{tool_info['name']}"] = module_info
                
    return modules_config

modules_config = load_module_config()


def check_if_module_exists(module_name, tool):
    key = f"{module_name}/{tool}"
    if key in modules_config.keys():
        return True, modules_config[key]
    return False, {}

def get_time_diff_in_minutes(iso_timestamp:str):
    diff = datetime.datetime.now() - datetime.datetime.fromisoformat(iso_timestamp)
    minutes, seconds = divmod(diff.total_seconds(), 60) 
    return int(minutes)

class ReturnMessage(BaseModel):
    success: bool = False
    info:Optional[str] 

class Input(BaseModel):
    name:str
    type:str

class Output(BaseModel):
    name:str
    type:str

class Parameters(BaseModel):
    name: str
    description: Optional[str]
    type:str
    required:bool


class Tool(BaseModel):
    name: str
    description: Optional[str]
    category:str
    input: List[Input]
    output: List[Output]
    parameters: List[Parameters]
    

class ModuleConfig(BaseModel):
    name: str
    description: Optional[str]
    tools: List[Tool]


# Enable CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event('startup')
async def startup():
    registry_manager.listen_for_modules()

@app.on_event("shutdown")
async def shutdown():
    registry_manager.close()



router_task = APIRouter(tags=["task"])

@router_task.get("/tasks", response_model=List[ModuleConfig])
async def get_tasks():
    available_modules_info = []
    registered_modules = list(registry_manager.get_available_modules().values())
   
    for registered_module in registered_modules:
        time_diff_minutes = get_time_diff_in_minutes(registered_module.last_seen)
        if time_diff_minutes<5:
            print(registered_module)
            module_exists, module_info = check_if_module_exists(registered_module.module, registered_module.tool)
            if module_exists:
                print(module_info)
                available_modules_info.append(ModuleConfig.parse_obj(module_info))

    return available_modules_info

class Request(BaseModel):
    name:str
    tool:str
    parameters:Optional[str] = Field("",description="Parameters needed for start tool")

@router_task.post("/task/start", response_model=ReturnMessage)
async def start_task(start_request:Request):
    module_name = f"{start_request.name}/{start_request.tool}"
    channel = f"/task/{start_request.name}/{start_request.tool}"
    if registry_manager.check_if_module_is_registered(module_name=module_name):
        module = registry_manager.get_module_data(module_name=module_name)
        if module.is_running:
            return ReturnMessage(success=False, info="task is already running")
        else:
            rps = PikaPubSub(queue_name=channel)
            message = {'cmd': "start" } 
            if len(start_request.parameters)>0:
                try:
                    parameters = json.loads(start_request.parameters.encode())
                    ## TODO Validate parameters here
                    message.update(parameters)
                except:
                    logger.exception("from parsing parameter json from start!!")
            
            if rps.publish(message=message):
                return ReturnMessage(success=True)
    else:
        ## Check with module conf if module exists 
        module_exists, _ = check_if_module_exists(module_name=start_request.name, tool=start_request.tool)
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module does not exist")


    

@router_task.post("/task/{name}/{tool}/pause", response_model=ReturnMessage)
async def pause_task(name, tool):
    module_name = f"{name}/{tool}"
    channel = f"/task/{name}/{tool}"
    if registry_manager.check_if_module_is_registered(module_name=module_name):
        module = registry_manager.get_module_data(module_name=module_name)
        if not module.is_running:
            return ReturnMessage(success=False, info="task is not running")
        else:
            rps = PikaPubSub(queue_name=channel)
            message = {'cmd': "pause" }
            
            if rps.publish(message=message):
                return ReturnMessage(success=True)
    else:
        ## Check with module conf if module exists 
        module_exists, _ = check_if_module_exists(module_name=name, tool=tool)
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module does not exist")

@router_task.post("/task/{name}/{tool}/resume", response_model=ReturnMessage)
async def resume_task(name, tool):
    module_name = f"{name}/{tool}"
    channel = f"/task/{name}/{tool}"
    if registry_manager.check_if_module_is_registered(module_name=module_name):
        module = registry_manager.get_module_data(module_name=module_name)
        if module.is_running:
            rps = PikaPubSub(queue_name=channel)
            message = {'cmd': "resume" }
            
            if rps.publish(message=message):
                return ReturnMessage(success=True)
        else:
            return ReturnMessage(success=False, info="task is not running")
            
    else:
        ## Check with module conf if module exists 
        module_exists, _ = check_if_module_exists(module_name=name, tool=tool)
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module does not exist")

@router_task.post("/task/{name}/{tool}/terminate", response_model=ReturnMessage)
async def terminate_task(name, tool):
    module_name = f"{name}/{tool}"
    channel = f"/task/{name}/{tool}"
    if registry_manager.check_if_module_is_registered(module_name=module_name):
        module = registry_manager.get_module_data(module_name=module_name)
        if not module.is_running:
            return ReturnMessage(success=False, info="task is not running")
        else:
            rps = PikaPubSub(queue_name=channel)
            message = {'cmd': "terminate" }
            
            if rps.publish(message=message):
                return ReturnMessage(success=True)
    else:
        ## Check with module conf if module exists 
        module_exists, _ = check_if_module_exists(module_name=name, tool=tool)
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module does not exist")




@router_task.get("/task/{name}/{tool}/stream-logs")
async def stream_task_logs(name, tool,request: Request):
    module_name = f"{name}/{tool}"
    channel = f"/task/{name}/{tool}"
    if registry_manager.check_if_module_is_registered(module_name=module_name):
        module = registry_manager.get_module_data(module_name=module_name)
        if not module.is_running:
            return ReturnMessage(success=False, info="task is not running")
        else:
            channel = f"/task/{name}/{tool}/logs"
            event_generator = log_consumer(request, channel) 
            return EventSourceResponse(event_generator)
    else:
        ## Check with module conf if module exists 
        module_exists, _ = check_if_module_exists(module_name=name, tool=tool)
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module does not exist")
    

app.include_router(router_task)

fastapi_port = int(os.environ.get("FASTAPI_PORT", "8070"))

class Server(uvicorn.Server):
    """Customized uvicorn.Server
    Uvicorn server overrides signals"""
    def handle_exit(self, sig: int, frame) -> None:
        return super().handle_exit(sig, frame)

async def main():
    server = Server(config=uvicorn.Config(app, workers=2, loop="asyncio", port=fastapi_port, host="0.0.0.0",log_level='info'))

    api = asyncio.create_task(server.serve())

    await asyncio.wait([api])

if __name__ == "__main__":
    asyncio.run(main())