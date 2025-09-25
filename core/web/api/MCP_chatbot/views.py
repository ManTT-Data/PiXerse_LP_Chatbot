from fastapi import APIRouter, HTTPException, Request

from core.schemas.chatbot_schemas import ChatbotQuery, ChatbotResponse

router = APIRouter()


@router.post("/chat", response_model=ChatbotResponse)
async def chat(query: ChatbotQuery, request: Request):
    try:
        chatbot = request.app.state.chatbot  # ✅ Lấy từ state (gán trong lifespan)
        response, tokens, tools_used, tools_response = await chatbot.process_query(
            query.query,
        )
        return {
            "response": response,
            "token_usage": tokens,
            "tools_used": tools_used,
            "tools_response": tools_response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))