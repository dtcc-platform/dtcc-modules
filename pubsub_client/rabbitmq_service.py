import os, pathlib, sys, json, uuid, time, asyncio, logging
import threading
import pika
import aio_pika

logging.getLogger("pika").setLevel(logging.WARNING)

project_dir = str(pathlib.Path(__file__).resolve().parents[0])
sys.path.append(project_dir)

from utils import try_except, ProgressBar
from logger import getLogger

logger = getLogger(__file__)

from base64 import b64encode, b64decode

rabbitmq_host =   os.environ.get("RABBITMQ_HOST", "localhost")
rabbitmq_user = os.environ.get("RABBITMQ_USER", "dtcc_rmq" )
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD", "dtcc_rmq")
rabbitmq_port = 5672

amq_url = f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:5672/"

async def log_consumer(request, queue_name = "test_queue") -> None:
    connection = await aio_pika.connect_robust(
        amq_url,
    )

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        # await channel.set_qos(prefetch_count=10)

        # Declaring queue
        queue = await channel.declare_queue(queue_name, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if await request.is_disconnected():
                    print("client disconnected!!!")
                    break
                async with message.process():
                    yield message.body.decode()

                    if queue.name in message.body.decode():
                        break
                time.sleep(0.01)
            

async def test_log_consumer(queue_name = "test_queue") -> None:
    connection = await aio_pika.connect_robust(
        amq_url,
    )

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        # await channel.set_qos(prefetch_count=10)

        # Declaring queue
        queue = await channel.declare_queue(queue_name, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:

                async with message.process():
                    print(json.loads(message.body.decode()))
                    # yield json.loads(message.body.decode())
                    if queue.name in message.body.decode():
                        break
                # time.sleep(0.5)


async def get_publish_channel():
    connection = await aio_pika.connect(amq_url)
    channel = await connection.channel()
    return channel

async def publish_async(channel:aio_pika.Channel, queue_name:str, msg:dict):
    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(msg).encode()),
        routing_key=queue_name,
    )

class PikaPubSub:

    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.creds = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        self.create_connection()
        
        
    def create_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host,port=rabbitmq_port, credentials=self.creds )
        )
        self.channel = self.connection.channel()
        logger.info('Pika connection established')
        
    def publish(self,message: dict):
        try:
            t = threading.Thread(target=self.___publish, args=(message,))

            t.start()
            return True
        except:
            logger.exception(f"from publish {message.__str__()}")
            return False

    @try_except(logger=logger)
    def ___publish(self, message: dict):
        """Method to publish message to RabbitMQ"""
        try:
            if self.channel.is_closed:
                self.channel = self.connection.channel()
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message).encode()
            )
        except:
            logger.exception(str(message))
            self.create_connection()
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message).encode()
            )

    def subscribe(self, on_mesage_callback):
        try:
            if self.channel.is_closed:
                print("creating channel!!")
                self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name)
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=on_mesage_callback)

            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.close_connection()
        except pika.exceptions.ConnectionWrongStateError:
            self.create_connection()
            self.subscribe(on_mesage_callback)
        except:
            logger.exception("from pubsub subscribe!!!!!!")
            

    @try_except(logger=logger)
    def close_connection(self):
        if (self.connection is not None):
            self.channel.close()
            self.connection.close()


    def __example_callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

class PikaProgressBar(ProgressBar):
    """Extends ProgressBar to allow you to use it straighforward on a script.
    Accepts an extra keyword argument named `stdout` (by default use sys.stdout)
    and may be any file-object to which send the progress status.
    """
    def __init__(self, module, tool, task_id, channel, *args, **kwargs):
        super(PikaProgressBar, self).__init__(*args, **kwargs)
        self.stdout = kwargs.get('stdout', sys.stdout)
        self.module = module
        self.tool = tool
        self.task_id = task_id
        self.client = PikaPubSub(queue_name=channel)

    def show_progress(self):
        if hasattr(self.stdout, 'isatty') and self.stdout.isatty():
            self.stdout.write('\r')
        else:
            self.stdout.write('\n')
        self.stdout.write(str(self))
        message = {"module": self.module, "tool": self.tool, "task_id":self.task_id, "progress":self.progress }
        self.client.publish(message=message)
        self.stdout.flush()

if __name__=='__main__':
    asyncio.run(test_log_consumer(queue_name='/task/dtcc/generate-citymodel/logs'))
    