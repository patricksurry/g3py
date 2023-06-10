from fastapi import FastAPI, Request, BackgroundTasks
from sse_starlette.sse import EventSourceResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager
import random
from apub import Publisher
import logging

# Illustrates an SSE endpoint to push events from an async data source to one or more clients


pub = Publisher()


async def datasource():
    """An async source producing sample events"""
    n = 0
    logging.debug('datasource starting')
    while True:
        line = f"count {n}"
        n += 1
        logging.debug(f"datasource: {line}")
        pub.publish(line)
        await asyncio.sleep(2 * random.random())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # kick off the datasource publisher on startup
    logging.debug('startup datasource')
    t = asyncio.create_task(datasource())
    logging.debug('startup complete')
    yield
    # shutdown
    t.cancel()
    logging.debug('shutdown datasource')


#create our app instance
app = FastAPI(lifespan=lifespan)

#add CORS so our web page can connect to our api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/stream')
async def apistream(request: Request, bg: BackgroundTasks):
    """Establish an SSE connection to push data to the client"""

    # subscribe to the datasource and unsubscribe when the client drops
    subid = pub.subscribe()
    bg.add_task(pub.unsubscribe, subid)

    async def dataclient():
        logging.debug('dataclient starting')
        while not await request.is_disconnected():
            logging.debug('dataclient yield')
            line = await pub.next(subid)
            yield line
        logging.debug("dataclient disconnected")

    return EventSourceResponse(dataclient())


#run the app
uvicorn.run(app, host="0.0.0.0", port=8888)
