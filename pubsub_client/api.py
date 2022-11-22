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

from logger import getLogger
from utils import try_except
from rabbitmq_service import PikaPubSub, log_consumer
from registry_manager import RegistryManager
from registry_manager import RegistryManager, ModuleRegistry

logger = getLogger(__file__)

pub_sub = PikaPubSub(queue_name="/task/run_sample_python_process")
pub_sub.publish(message={"cmd":"start"})

app = FastAPI(
    title="DTCC Core demo API",
    description="API for db access and communication",
    version="1.0"
)

registry_manager = RegistryManager()

class ReturnMessage(BaseModel):
    success: bool = False
    info:Optional[str] 

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

@router_task.get("/tasks", response_model=List[ModuleRegistry])
async def get_tasks():
    ## Check with module conf if module exists 
    data = registry_manager.get_available_modules().items()
    return data

@router_task.post("/task/{name}/{command}/start", response_model=ReturnMessage)
async def start_task(name, command):
    modules = registry_manager.get_available_modules()
    module_names = modules.keys()
    module_name = f"{name}/{command}"
    channel = f"/task/{name}/{command}"
    if module_name in module_names:
        module = modules[module_name]
        if module.is_running:
            return ReturnMessage(success=False, info="task is already running")
        else:
            rps = PikaPubSub(queue_name=channel)
            message = {'cmd': "start" }
            
            if rps.publish(message=message):
                return ReturnMessage(success=True)
    else:
        ## Check with module conf if module exists 
        module_exists = True
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module is not online")


    

@router_task.post("/task/{name}/{command}/pause", response_model=ReturnMessage)
async def pause_task(name, command):
    modules = registry_manager.get_available_modules()
    module_names = modules.keys()
    module_name = f"{name}/{command}"
    channel = f"/task/{name}/{command}"
    if module_name in module_names:
        module = modules[module_name]
        if not module.is_running:
            return ReturnMessage(success=False, info="task is not running")
        else:
            rps = PikaPubSub(queue_name=channel)
            message = {'cmd': "pause" }
            
            if rps.publish(message=message):
                return ReturnMessage(success=True)
    else:
        ## Check with module conf if module exists 
        module_exists = True
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module is not online")

@router_task.post("/task/{name}/{command}/resume", response_model=ReturnMessage)
async def resume_task(name, command):
    modules = registry_manager.get_available_modules()
    module_names = modules.keys()
    module_name = f"{name}/{command}"
    channel = f"/task/{name}/{command}"
    if module_name in module_names:
        module = modules[module_name]
        if module.is_running:
            rps = PikaPubSub(queue_name=channel)
            message = {'cmd': "resume" }
            
            if rps.publish(message=message):
                return ReturnMessage(success=True)
        else:
            return ReturnMessage(success=False, info="task is not running")
            
    else:
        ## Check with module conf if module exists 
        module_exists = True
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module is not online")

@router_task.post("/task/{name}/{command}/terminate", response_model=ReturnMessage)
async def terminate_task(name, command):
    modules = registry_manager.get_available_modules()
    module_names = modules.keys()
    module_name = f"{name}/{command}"
    channel = f"/task/{name}/{command}"
    if module_name in module_names:
        module = modules[module_name]
        if not module.is_running:
            return ReturnMessage(success=False, info="task is not running")
        else:
            rps = PikaPubSub(queue_name=channel)
            message = {'cmd': "terminate" }
            
            if rps.publish(message=message):
                return ReturnMessage(success=True)
    else:
        ## Check with module conf if module exists 
        module_exists = True
        if module_exists:
            return ReturnMessage(success=False, info="module is not online")
        else:
            return ReturnMessage(success=False, info="module is not online")




@router_task.get("/task/{name}/{command}/stream-logs")
async def stream_task_logs(name, command,request: Request):
    modules = registry_manager.get_available_modules()
    module_names = modules.keys()
    module_name = f"{name}/{command}"
    channel = f"/task/{name}/{command}/logs"
    event_generator = log_consumer(request, channel) 
    return EventSourceResponse(event_generator)

app.include_router(router_task)

fastapi_port = int(os.environ.get("FASTAPI_PORT", "8070"))

class Server(uvicorn.Server):
    """Customized uvicorn.Server
    
    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""
    def handle_exit(self, sig: int, frame) -> None:
        return super().handle_exit(sig, frame)

async def main():
    "Run Rocketry and FastAPI"
    server = Server(config=uvicorn.Config(app, workers=2, loop="asyncio", port=fastapi_port, host="0.0.0.0",log_level='info'))

    api = asyncio.create_task(server.serve())

    await asyncio.wait([api])

if __name__ == "__main__":
    asyncio.run(main())