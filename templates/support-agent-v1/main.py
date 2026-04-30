from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os
from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from tools import available_tools
from memory import conversation_memory

app = FastAPI(
    title="Smart Support UA Pro v1",
    description="Розумний агент підтримки з контекстною пам'яттю",
    version="1.0.0"
)

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7,
)

class UserMessage(BaseModel):
    message: str = Field(..., description="Повідомлення клієнта")
    customer_name: str = Field("Клієнт", description="Ім'я клієнта")
    order_id: Optional[str] = Field(None, description="Номер замовлення")
    phone: Optional[str] = Field(None, description="Телефон")

@app.post("/chat")
async def chat_with_support(msg: UserMessage):
    try:
        # Додаємо поточне повідомлення в пам'ять
        conversation_memory.add_message("user", msg.message, msg.customer_name)

        support_agent = Agent(
            role="Головний агент підтримки українського онлайн-магазину",
            goal="Надати максимально корисну, емпатичну та професійну допомогу клієнту",
            backstory="Ти висококваліфікований спеціаліст підтримки з багаторічним досвідом. Ти завжди намагаєшся вирішити проблему клієнта швидко і приємно.",
            verbose=True,
            llm=llm,
            tools=list(available_tools.values()),
            allow_delegation=True
        )

        task = Task(
            description=f"""
            Клієнт: {msg.customer_name}
            Повідомлення: "{msg.message}"
            {f"Номер замовлення: {msg.order_id}" if msg.order_id else ""}
            {f"Телефон: {msg.phone}" if msg.phone else ""}

            {conversation_memory.get_formatted_history()}

            Дай природну, ввічливу та корисну відповідь українською мовою.
            Якщо потрібно — використовуй інструменти.
            Якщо запит складний — підготуй ескалацію менеджеру з коротким самарі.
            """,
            agent=support_agent,
            expected_output="Природна українська відповідь клієнту"
        )

        crew = Crew(
            agents=[support_agent],
            tasks=[task],
            verbose=2
        )

        result = crew.kickoff()

        # Зберігаємо відповідь агента в пам'ять
        conversation_memory.add_message("assistant", str(result), msg.customer_name)

        return {
            "status": "success",
            "response": str(result),
            "agent": "Smart Support UA Pro",
            "customer_name": msg.customer_name
        }

    except Exception as e:
        print(f"Agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Помилка при обробці запиту: {str(e)}"
        )


@app.get("/")
async def root():
    return {
        "message": "Smart Support UA Pro v1 is running",
        "version": "1.0.0",
        "status": "active",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)