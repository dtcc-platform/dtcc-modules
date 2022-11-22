import time, pathlib, sys, asyncio


project_dir = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.append(project_dir)


from rabbitmq_service import test_log_consumer


if __name__=='__main__':
    asyncio.run(test_log_consumer(queue_name='/task/run_sample_python_process/logs'))