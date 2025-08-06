import os
import re
import asyncio
from typing import Optional, Annotated
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agents import Agent, Runner, set_tracing_disabled, function_tool
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from session import PostgreSQLSession, init_db  # ✅ Your SQLAlchemy session class
from models import AgentSession  # 👈 Import the model to register it

# ========== Environment ==========
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing in .env")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL = "gemini-2.0-flash"

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL)
model = OpenAIChatCompletionsModel(model=GEMINI_MODEL, openai_client=external_client)

# ========== Pydantic Models ==========
class MenuOut(BaseModel):
    Burger: int
    Fries: int
    Coke: int
    Deal: int

PhoneField = Annotated[
    Optional[str],
    Field(default=None, description="Customer phone number")
]

class OrderIn(BaseModel):
    Burger: int = 0
    Fries: int = 0
    Coke: int = 0
    Deal: int = 0
    phone: str = "unknown"

class OrderDetails(BaseModel):
    order_type: str
    text: str = ""

class LastOrderIn(BaseModel):
    reference: str = ""

# ========== Function Tools ==========
@function_tool
def get_menu() -> MenuOut:
    return MenuOut(Burger=300, Fries=150, Coke=100, Deal=500)

@function_tool
def create_order(order: OrderIn) -> str:
    total = (
        order.Burger * 300 +
        order.Fries * 150 +
        order.Coke * 100 +
        order.Deal * 500
    )
    ordered = {k: v for k, v in order.dict().items() if v and k != "phone"}
    phone = order.phone or "unknown"
    print(f"📦 Order: {ordered} (Phone: {phone})")
    return f"✅ Order confirmed: {ordered}. Total: {total} PKR. Estimated delivery: 20 minutes."

@function_tool
def parse_order(text: str) -> OrderIn:
    counts = {"burger": 0, "fries": 0, "coke": 0, "deal": 0}
    synonyms = {
        "burger": {"burger", "chicken burger"},
        "fries": {"fries", "chips"},
        "coke": {"coke", "cola", "sprite", "pepsi"},
        "deal": {"deal", "combo"},
    }
    numbers = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    }

    words = re.findall(r"\w+", text.lower())
    for i, word in enumerate(words):
        for key, aliases in synonyms.items():
            if word in aliases:
                qty = 1
                if i > 0 and words[i - 1] in numbers:
                    qty = numbers[words[i - 1]]
                counts[key] += qty

    phone_match = re.search(r"\b03\d{9}\b", text.replace("-", ""))
    phone = phone_match.group(0) if phone_match else "unknown"

    return OrderIn(**counts, phone=phone)

@function_tool
def get_status(order_id: str) -> str:
    return f"🕒 Order {order_id} is being prepared!"

@function_tool
def get_order_details(details: OrderDetails) -> str:
    text = details.text.lower()
    phone_match = re.search(r'\b(03\d{9})\b', text)
    phone = phone_match.group(1) if phone_match else "unknown"
    address = text.split(phone)[0].strip() if phone != "unknown" else "unknown"
    t = details.order_type.lower()

    if t == "delivery":
        return f"🛵 Order to {address}. Contact: {phone}"
    elif t == "dine-in":
        return "🍽️ Dine-in confirmed."
    elif t == "take-away":
        return "🥡 Take-away confirmed."
    else:
        return "❌ Invalid type. Choose delivery, dine-in, or take-away."

@function_tool
async def get_last_order_info(info: LastOrderIn) -> str:
    return "🔍 This version does not support order history."

# ========== Agent Setup ==========
set_tracing_disabled(True)

fastfood_agent = Agent(
    name="FastFoodBot",
    instructions="""
You are a friendly Pakistani fast-food assistant.
- Greet with 'Asalam-o-Alaikum! Khairiyat? Ready to order?'
- Use parse_order on messages before creating orders.
- Ask if order is for delivery, dine-in, or take-away.
- Remember previous conversation and act like a human waiter.
- get_last_order_info returns a static message (no DB).
- Always thank the customer at the end.
""",
    tools=[
        get_menu,
        create_order,
        get_status,
        parse_order,
        get_order_details,
        get_last_order_info
    ],
    model=model
)

# ========== Main Loop ==========
async def main():
    print("🍔 FastFoodBot ready! Type 'quit' to exit.\n")

    await init_db()

    session = PostgreSQLSession()
    previous = await session.load()
    chat_history = previous.chat_conversation if previous else ""
    order_detail = previous.order_detail if previous else ""

    if previous:
        print("📜 Previous session restored.")
        print(f"🗨️  Chat: {chat_history}")
        print(f"🧾 Order: {order_detail}")

    while True:
        user_input = input("🍔 You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("👋 Goodbye!")
            break

        chat_history += f"\n👤: {user_input}"

        result = await Runner.run(fastfood_agent, chat_history)
        bot_reply = result.final_output
        print(f"🤖 Bot: {bot_reply}")

        chat_history += f"\n🤖: {bot_reply}"

        if "order confirmed" in bot_reply.lower():
            order_detail = bot_reply

        await session.save(chat_history.strip(), order_detail.strip())

if __name__ == "__main__":
    asyncio.run(main())
#==========================================
# 👆 all your existing imports and code are unchanged ...

# ========== Main Loop ========== (unchanged)
async def main():
    print("🍔 FastFoodBot ready! Type 'quit' to exit.\n")

    await init_db()

    session = PostgreSQLSession()
    previous = await session.load()
    chat_history = previous.chat_conversation if previous else ""
    order_detail = previous.order_detail if previous else ""

    if previous:
        print("📜 Previous session restored.")
        print(f"🗨️  Chat: {chat_history}")
        print(f"🧾 Order: {order_detail}")

    while True:
        user_input = input("🍔 You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("👋 Goodbye!")
            break

        chat_history += f"\n👤: {user_input}"

        result = await Runner.run(fastfood_agent, chat_history)
        bot_reply = result.final_output
        print(f"🤖 Bot: {bot_reply}")

        chat_history += f"\n🤖: {bot_reply}"

        if "order confirmed" in bot_reply.lower():
            order_detail = bot_reply

        await session.save(chat_history.strip(), order_detail.strip())

# ========== FastAPI Setup =========================================================================================================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="🍔 FastFood Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to FastFoodBot API"}

@app.get("/menu")
async def get_menu_api():
    return get_menu()

@app.get("/status/{order_id}")
async def get_status_api(order_id: str):
    return {"status": get_status(order_id)}

class UserMessage(BaseModel):
    message: str

@app.post("/order")
async def chat_with_agent(user_msg: UserMessage):
    session = PostgreSQLSession()
    previous = await session.load()
    chat_history = previous.chat_conversation if previous else ""
    order_detail = previous.order_detail if previous else ""

    chat_history += f"\n👤: {user_msg.message}"

    result = await Runner.run(fastfood_agent, chat_history)
    bot_reply = result.final_output
    chat_history += f"\n🤖: {bot_reply}"

    if "order confirmed" in bot_reply.lower():
        order_detail = bot_reply

    await session.save(chat_history.strip(), order_detail.strip())
    return {"reply": bot_reply}

# ========== Entry Point ==========

if __name__ == "__main__":
    import sys
    if "api" in sys.argv:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        asyncio.run(main())
