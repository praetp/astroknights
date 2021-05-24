import websockets

import asyncio
import json
import time

class WSServer():
    
    def __init__(self, context, mpucontroller):
        print("WSServer: INIT")
        self._context = context
        self.mpucontroller=mpucontroller
        start_server = websockets.serve(self.handler, "0.0.0.0", 8001)
        asyncio.get_event_loop().run_until_complete(start_server)
        self.data={}

    def updateData(self, data):
        self.data=data

    async def producer(self):
        global steering
        await asyncio.sleep(1)
        ret =  json.dumps(
            {
                "tick": time.time(),
                "data": self.data
            })
        return ret
            
    async def consumer(self, a):
        r = json.loads(a)
        print("WSServer" + str(r))
        if "calibrate" in r:
            print("CALIBRATE")
            self.mpucontroller.calibrate()
            pass

    async def consumer_handler(self, websocket, path):
        print("WSServer: New ConsumerHandler")
        try:
            async for message in websocket:
                await self.consumer(message)
        except websockets.exceptions.ConnectionClosedError:
            print("WSServer: ConsumerHandler Error")
            
    async def producer_handler(self, websocket, path):
        print("WSServer: New ProducerHandler")
        while True:
            message = await self.producer()
            await websocket.send(message)
            
    async def handler(self, websocket, path):
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket, path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        print("WSServer: New DONE")
        for task in pending:
            task.cancel()

