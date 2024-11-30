from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from graph import getGraph
import os

app = FastAPI()

class ChatRequest(BaseModel):
    messages: list
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

@app.post("/generate-vector")
async def generateVector():
    try:
        loader = PyPDFLoader("https://my-chatbot-deployment-bucket.s3.ap-southeast-1.amazonaws.com/masterigrandview.pdf")

        #Load the document by calling loader.load()
        pages = loader.load()

        # 2. Splitter
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len
        )

        docs = text_splitter.split_documents(pages)
        embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        )

        persist_directory = './docs/chroma/'

        vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=persist_directory
        )

        return {"message": 'done'}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 43610))  # Lấy cổng từ môi trường, mặc định là 8000
    uvicorn.run(app, host="0.0.0.0", port=port)