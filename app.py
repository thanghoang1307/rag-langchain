from fastapi import FastAPI, HTTPException
from typing import Dict
from graph import getGraph

app = FastAPI()

class ChatRequest(BaseModel):
    question: str
    thread_id: str

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    question = chat_request.question
    threadId = chat_request.thread_id
    try:
        graph = getGraph()
        config = {"configurable": {"thread_id": threadId}}
        response = await graph.ainvoke({"messages": [{"role": "user", "content": question}]},config=config)
        return jsonify({"answer": response["messages"][-1].content})
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Lấy cổng từ môi trường, mặc định là 8000
    uvicorn.run(app, host="0.0.0.0", port=port)