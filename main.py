from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import logging
from callback import StreamingLLMCallbackHandler
from schemas import ChatResponse
from lorem.text import TextLorem

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory=Path(__file__).parent.absolute() / "static"), name="static", )


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def generate_random_sentence():
    lorem = TextLorem(srange=(3, 45))
    sentence = lorem.sentence()
    return sentence.split()


async def agent_astep(callback_my):
    for i in await generate_random_sentence():
        await callback_my.on_llm_new_token(i)
        await callback_my.on_llm_new_token(' ')


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    callback_my = StreamingLLMCallbackHandler(websocket)
    resp = ChatResponse(sender="bot", message='', type="start")
    await websocket.send_json(resp.dict())

    while True:
        try:

            # helper_agent.determine_conversation_stage()
            await agent_astep(callback_my)
            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())
            question = await websocket.receive_text()
            resp = ChatResponse(sender="you", message=question, type="stream")

            await websocket.send_json(resp.dict())
            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())

        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(sender="bot", message="Sorry, something went wrong. Try again.", type="error", )
            await websocket.send_json(resp.dict())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
