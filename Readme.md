
# Hướng dẫn

## Cấu trúc file và thư mục

1. jupyter_notebook: chứa các file notebook
- generate_vector: Convert file pdf từ thư mục knowledge_pdf và lưu vào Chroma vector store chứa tại thư mục docs
- app: Code RAG Chatbot tạo phản hồi từ query của user
2. docs: Vector store được tạo từ package Chroma
3. knowledge_pdf: chứa các file pdf knowledge
4. app.py: API Endpoint
5. graph.py: Code RAG Chatbot tạo phản hồi từ query của user
6. requirements.txt: các thư viện cần cài đặt

## Tài liệu MKT:
RAG Chatbot Concept Idea: https://masterisegroup-my.sharepoint.com/:p:/g/personal/thang_hoang_masterisehomes_com/EQh9aFdH9ShHq79ZjcwPPRwBYxl_7AIkXuFQb5YU1gv_8Q?e=UfGCZI
Link demo chatbot: https://www.facebook.com/messages/t/101142756401997

## Tài liệu tham khảo:
https://python.langchain.com/docs/tutorials/rag/
https://python.langchain.com/docs/tutorials/qa_chat_history/