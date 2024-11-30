from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import getGraph
import os

app = FastAPI()

class ChatRequest(BaseModel):
    messages: dict
    thread_id: str

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    messages = chat_request.messages
    threadId = chat_request.thread_id
    try:
        graph = await getGraph()
        config = {"configurable": {"thread_id": threadId}}
        response = await graph.ainvoke({"messages": messages},config=config)
        return {"answer": response["messages"][-1].content}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 43610))  # Lấy cổng từ môi trường, mặc định là 8000
    uvicorn.run(app, host="0.0.0.0", port=port)