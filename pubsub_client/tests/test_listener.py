import time, pathlib, sys


project_dir = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.append(project_dir)

from rabbitmq_service import PikaPubSub

def test():

    pub_sub = PikaPubSub(queue_name="/task/run_sample_python_process")
    pub_sub.publish(message={"cmd":"start"})

    time.sleep(1)

    pub_sub.publish(message={"cmd":"pause"})
    for i in range(3):
        print(i)
        time.sleep(1)

    pub_sub.publish(message={"cmd":"resume"})
    for i in range(2):
        print(i)
        time.sleep(1)

    pub_sub.publish(message={"cmd":"terminate"})



if __name__=='__main__':
    test()