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
    # loader = PyPDFLoader("https://my-chatbot-deployment-bucket.s3.ap-southeast-1.amazonaws.com/masterigrandview.pdf")

    #Load the document by calling loader.load()
    # pages = loader.load()

    # 2. Splitter

    # text_splitter = CharacterTextSplitter(
    #     separator="\n",
    #     chunk_size=1000,
    #     chunk_overlap=150,
    #     length_function=len
    # )

    # docs = text_splitter.split_documents(pages)

    # 3. Vector store
    # load_dotenv()

    # if not os.getenv("OPENAI_API_KEY"):
    #     os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

    # os.environ["LANGSMITH_TRACING_V2"] = "true"
    # if not os.getenv("LANGSMITH_API_KEY"):
    #     os.environ["LANGSMITH_API_KEY"] = getpass.getpass()

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )

    persist_directory = './docs/chroma/'

    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    print("Loaded existing vector store.")

    # vectordb = Chroma.from_documents(
    #         documents=docs,
    #         embedding=embeddings,
    #         persist_directory=persist_directory
    #     )

    # try:
    #     # Try to load the existing vector store
    #     vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    #     print("Loaded existing vector store.")
    # except Exception as e:
    #     # Create the vector store
    #     vectordb = Chroma.from_documents(
    #         documents=docs,
    #         embedding=embeddings,
    #         persist_directory=persist_directory
    #     )

    # Memory
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    graph_builder = StateGraph(MessagesState)

    @tool(response_format="content_and_artifact")
    def retrieve(query: str):
        """Retrieve information related to a query."""
        retrieved_docs = vectordb.similarity_search(query, k=2)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    # Step 1: Generate an AIMessage that may include a tool-call to be sent.
    def query_or_respond(state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = llm.bind_tools([retrieve])
        system_message_content = (
            "Bạn là nhân viên chăm sóc khách hàng của Masterise Homes và bạn sẽ trả lời các câu hỏi của khách hàng về Công ty cũng như các dự án thuộc Công ty."
            "Hãy dùng đại từ xưng hô gọi khách hàng là Anh/Chị, còn bạn dùng đại từ xưng hô là Em."
            "Hãy trả lời câu hỏi của khách hàng một cách lịch sự và tôn trọng."
            "Trong trường hợp khách hàng hỏi những câu hỏi không liên quan đến Công ty và dự án, hãy từ chối trả lời một cách lịch sự."
            "Không bao giờ được hỏi khách hỏi xong chưa và xin phép dừng cuộc hội thoại"
            "\n\n"
        )
        response = llm_with_tools.invoke([SystemMessage(system_message_content)] + state["messages"])
        # MessagesState appends messages to state instead of overwriting
        return {"messages": [response]}

    # Step 2: Execute the retrieval.
    tools = ToolNode([retrieve])

    # Step 3: Generate a response using the retrieved content.
    def generate(state: MessagesState):
        """Generate answer."""
        # Get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]

        # Format into prompt
        docs_content = "\n\n".join(doc.content for doc in tool_messages)
        system_message_content = (
            "Bạn là nhân viên chăm sóc khách hàng của Masterise Homes và bạn sẽ trả lời các câu hỏi của khách hàng về Công ty cũng như các dự án thuộc Công ty."
            "Hãy dùng đại từ xưng hô gọi khách hàng là Anh/Chị, còn bạn dùng đại từ xưng hô là Em."
            "Hãy trả lời câu hỏi của khách hàng một cách lịch sự và tôn trọng."
            "Trong trường hợp khách hàng hỏi những câu hỏi không liên quan đến Công ty và dự án, hãy từ chối trả lời một cách lịch sự."
            "Không bao giờ được hỏi khách hỏi xong chưa và xin phép dừng cuộc hội thoại"
            "\n\n"
            f"{docs_content}"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
            or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages

        # Run
        response = llm.invoke(prompt)
        return {"messages": [response]}

    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    return graph