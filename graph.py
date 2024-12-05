# https://medium.com/@onkarmishra/using-langchain-for-question-answering-on-own-data-3af0a82789ed
# 1. Load document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from dotenv import load_dotenv
import getpass
import os

async def getGraph():
    # load_dotenv()
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )

    persist_directory = 'docs/chroma/'

    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    # Memory
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    graph_builder = StateGraph(MessagesState)

    def generate(state: MessagesState):
        """Generate answer."""
        # Get generated ToolMessages
        query = state["messages"][-1].content
        retrieved_docs = vectordb.similarity_search(query, k=2)
        
        # Format into prompt
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
        system_message_content = (
            "Bạn là nhân viên chăm sóc khách hàng của dự án Masteri Grand View và bạn sẽ trả lời các câu hỏi của khách hàng về dự án Masteri Grand View."
            "Hãy dùng đại từ xưng hô gọi khách hàng là Anh/Chị, còn bạn dùng đại từ xưng hô là Em."
            "Hãy trả lời câu hỏi của khách hàng một cách lịch sự và tôn trọng."
            "Chỉ dựa trên thông tin trong tài liệu dự án Masteri Grand View bên dưới, trả lời câu hỏi:"
            "\n\n"
            f"{docs_content}"
            "\n\n"
            "Trong trường hợp khách hàng hỏi những câu hỏi không liên quan đến Công ty và dự án, hãy từ chối trả lời một cách lịch sự."
            "Nếu thông tin không có trong tài liệu, hãy trả lời với khách hàng rằng thông tin này bạn không rõ và nói khách hàng gọi cho bộ phận kinh doanh"
            "Không bao giờ sáng tạo nội dung"
        )
        conversation_messages = [
            message
            for message in state["messages"]
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages

        # Run
        response = llm.invoke(prompt)
        return {"messages": [response]}

    # Graph builder
    graph_builder.add_node(generate)
    graph_builder.set_entry_point("generate")
    graph_builder.add_edge("generate", END)
    # memory = MemorySaver()
    # graph = graph_builder.compile(checkpointer=memory)
    graph = graph_builder.compile()
    return graph