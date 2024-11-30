import json
from graph import getGraph
import asyncio

async def getAnswer(question, thread_id):
    graph = await getGraph()
    config = {"configurable": {"thread_id": thread_id}}
    answer = await graph.ainvoke({"messages": [{"role": "user", "content": question}]}, config=config)
    return answer

async def lambda_handler(event, context):
    # Parse body nếu là JSON
    body = json.loads(event['body'])
    
    question = body.get('question')
    thread_id = body.get('thread_id')
    
    try:
        answer = asyncio.run(getAnswer(question, thread_id))
        
        response = {
        'statusCode': 200,
        'body': json.dumps({
            'answer': answer,
        })
    }
        return response
    except Exception as e:
        return {"error": str(e)}