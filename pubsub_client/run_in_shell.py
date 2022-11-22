import subprocess, shlex, logging, time, pathlib, sys, os, threading, signal, traceback, json

from abc import ABC, abstractmethod

project_dir = str(pathlib.Path(__file__).resolve().parents[0])
sys.path.append(project_dir)

from logger import getLogger
from utils import try_except
from rabbitmq_service import PikaPubSub
from registry_manager import RegistryManager

logger = getLogger(__file__)



class RunInShell(ABC):
    def __init__(self,module, command, publish=True,shell_command="ls") -> None:
        self.module = module
        self.module_command = command
        self.channel = f"/task/{module}/{command}"
        self.logs_channel = f"/task/{module}/{command}/logs"

        self.publish = publish
        if publish: 
            self.pika_pub_sub = PikaPubSub(queue_name=self.channel)
            self.pika_log_pub = PikaPubSub(queue_name=self.logs_channel)
            self.registry_manager = RegistryManager()
        self.process = None
        self.shell_command = shell_command
        self.is_process_running = False

    @try_except(logger=logger)
    def listen(self):
        registry_scheduler = threading.Thread(target=self.register_on_schedule)
        registry_scheduler.start()
        try:
            while True:
                logger.info(f"Waiting for  {self.channel}")
                self.pika_pub_sub.subscribe(self.consume)
        except BaseException:
            logger.exception("from RunInShell")
            sys.exit(1)


    def register_on_schedule(self,minutes=1):
        while True:
            self.registry_manager.register_module(module=self.module,command=self.module_command, status="ok", is_running=self.is_process_running)
            time.sleep(minutes*60)
        

    def consume(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

        if body is not None: 
            message = json.loads(body)
            logger.info("received meassge: "+ str(message))
            if type(message) is dict:
                command = message.get("cmd","")

                if command == 'start':
                    self.shell_command = self.process_arguments_on_start(message=message)
                    self.start()
                    message = {'status':'started'}
                    self.pika_log_pub.publish(message=json.dumps(message))
                    self.pika_pub_sub.publish(message=json.dumps(message))

                elif command == 'pause':
                    self.pause()
                    message = {'status':'paused'}
                    self.pika_log_pub.publish(message=json.dumps(message))
                    self.pika_pub_sub.publish(message=json.dumps(message))

                elif command == 'resume':
                    self.resume()
                    message = {'status':'resumed'}
                    self.pika_log_pub.publish(message=json.dumps(message))
                    self.pika_pub_sub.publish(message=json.dumps(message))

                elif command == 'terminate':
                    self.terminate()
                    message = {'status':'terminated'}
                    self.pika_log_pub.publish(message=json.dumps(message))
                    self.pika_pub_sub.publish(message=json.dumps(message))

                elif command == "close_client_loop":   
                    message = {'status':'closed_client_loop'}
                    self.pika_log_pub.publish(message=json.dumps(message))
                    self.pika_pub_sub.publish(message=json.dumps(message))
                    self.close()
                    sys.exit(0)

        return

    def start(self):
        shell_command_args = shlex.split(self.shell_command)

        logger.info('Subprocess: "' + self.shell_command + '"')

        try:
            logger.info(self.channel + ":" +'starting process')
    
            if self.publish:
                self.pika_log_pub.publish( message={'info': 'starting process'})

            self.process = subprocess.Popen(
                shell_command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) 
         
            stdout_thread = threading.Thread(target=self.__capture_stdout, args=(self.process,))
            stdout_thread.start()
            logger.info(self.channel + ":" +'start succeded!')
            if self.publish:
                self.pika_log_pub.publish( message={'info': 'start succeded!'})
            return True
       
        except BaseException:
            error = traceback.format_exc()
            logger.exception(self.channel + ":" +'Exception occured while starting subprocess')
            if self.publish:
                self.pika_log_pub.publish( message={'error': 'Exception occured while starting subprocess: \n' + str(error)})
            return False
       
    def terminate(self):
        try:
            if self.process is not None:
                logger.info(self.channel + ":" +'terminating process')
                if self.publish:
                    self.pika_log_pub.publish( message={'info': 'terminating process'})

                self.process.terminate()
                if self.process.poll() is None:
                    self.process.kill()
                    # os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                logger.info(self.channel + ":" +'terminate succeded!')
                if self.publish:
                    self.pika_log_pub.publish( message={'info': 'terminate succeded!'})
                self.is_process_running = False
                return True

        except BaseException:
            error = traceback.format_exc()
            logger.exception(self.channel + ":" +'Exception occured while terminating subprocess')
    
            if self.publish:
                self.pika_log_pub.publish( message={'error': 'Exception occured while terminating subprocess: \n  ' + error})
       
        return False

    def pause(self):
        try:
            if self.process is not None:
                if self.process.poll() is None:
                    logger.info(self.channel + ":" +'pausing process')
    
                    if self.publish:
                        self.pika_log_pub.publish( message={'info': 'pausing process'})

                    self.process.send_signal(signal.SIGSTOP)

                    logger.info(self.channel + ":" +'pause succeded!')
                    if self.publish:
                        self.pika_log_pub.publish( message={'info': 'pause succeded!'})
                    self.is_process_running = False
                    return True
        except BaseException:
            error = traceback.format_exc()
            logger.exception(self.channel + ":" +'Exception occured while pausing subprocess')
    
            if self.publish:
                self.pika_log_pub.publish( message={'error': 'Exception occured while pausing subprocess: \n  ' + error})
       
        return False

    def resume(self):
        try:
            if self.process is not None:
                if self.process.poll() is None:
                    logger.info(self.channel + ":" +'resuming process')
    
                    if self.publish:
                        self.pika_log_pub.publish( message={'info': 'resuming process'})

                    self.process.send_signal(signal.SIGCONT)
                    os.kill(self.process.pid, signal.SIGCONT)
                    

                    logger.info(self.channel + ":" +'resume succeded!')
                    if self.publish:
                        self.pika_log_pub.publish( message={'info': 'resume succeded!'})
                    self.is_process_running = True
                    return True

        except BaseException:
            error = traceback.format_exc()
            logger.exception(self.channel + ":" +'Exception occured while resuming subprocess')
    
            if self.publish:
                self.pika_log_pub.publish( message={'error': 'Exception occured while resuming subprocess: \n  ' + error})
        
       
        return False
        
    def close(self):
        self.terminate()
        if self.pika_log_pub is not None:
            self.pika_log_pub.close_connection()
        if self.pika_pub_sub is not None:
            self.pika_pub_sub.close_connection()
        
    def __capture_stdout(self, process: subprocess.Popen):
        self.is_process_running = True
       
        try:
            while process.poll() is None:
                output = process.stdout.read1().decode('utf-8')
                for i, line in enumerate(output.strip().split('\n')):
                    if len(line.strip())>0:
                        if self.publish:
                            self.pika_log_pub.publish( message={'log':line})
                        logger.info(self.channel + ": " +line)
                time.sleep(0.1)
            if self.publish:
                self.pika_log_pub.publish( message={'info': 'Task succeded!'})
            self.on_success()

        except BaseException:
            error = traceback.format_exc()
            logger.exception(self.channel + ":" +'Exception occured while capturing stdout from subprocess')

            self.on_failure()
            if self.publish:
                self.pika_log_pub.publish( message={'error': 'Exception occured while capturing stdout from subprocess: \n  ' + error})
        finally:
            self.is_process_running = False

    def on_success(self):
        return_data = self.process_return_data()
        # NOTE maybe handle results here?
        
        message = json.dumps({'status':'success', 'data':return_data})
        logger.info(self.channel + message)

        if self.publish:
            time.sleep(0.5)
            self.pika_log_pub.publish( message=message)
    

  
    def on_failure(self, error):
        logger.info(self.channel + ": Failed!")
        message = json.dumps({'status':'failed', "error":error})
        if self.publish:
            time.sleep(0.5)
            self.pika_log_pub.publish( message=message)

    @abstractmethod    
    def process_return_data(self):
        return "dummy result"

    
    @abstractmethod
    def process_arguments_on_start(self, message:dict) -> str:
        """
        Pass in arguments based on the recived message if needed
        Otherwise just return the original shell command
        """
        return self.shell_command


class SamplePythonProcessRunner(RunInShell):
    def __init__(self, publish=False) -> None:
        sample_logger_path = os.path.join(project_dir, "tests/sample_logging_process.py")
        command=f'python3 {sample_logger_path}'

        RunInShell.__init__(self,
            task_name="run_sample_python_process",
            publish=publish,
            shell_command=command
        )

    def process_arguments_on_start(self, message:dict):
        return self.shell_command

    def process_return_data(self):
        return "dummy result"

def test_run_in_shell(publish=False):
    sample_logger_path = os.path.join(project_dir, "src/tests/sample_logging_process.py")
    command=f'python3 {sample_logger_path}'

    run_in_shell = SamplePythonProcessRunner(publish=publish)

    run_in_shell.start(command=command)
    time.sleep(1)

    if run_in_shell.pause():
        for i in range(3):
            print(i)
            time.sleep(1)

    if run_in_shell.resume():
        for i in range(2):
            print(i)
            time.sleep(1)

    run_in_shell.terminate()


if __name__=="__main__":
    # test_run_in_shell(publish=False)
    sample_process = SamplePythonProcessRunner(publish=True)
    sample_process.listen()