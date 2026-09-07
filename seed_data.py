# seed_data.py
from app.database import SessionLocal
from app.models.user import User
from app.models.agent import Agent
from app.models.purchase import Purchase
from app.models.chat import ChatMessage
from datetime import datetime, timedelta
import random

def seed_dashboard():
    db = SessionLocal()
    
    users = db.query(User).all()
    if not users:
        print('❌ No users found!')
        return
    user = users[0]
    
    # 1. Створюємо агентів
    agents_data = [
        {'name': 'Support Bot', 'role': 'Support', 'status': 'active', 'price': 10},
        {'name': 'Sales Assistant', 'role': 'Sales', 'status': 'active', 'price': 15},
        {'name': 'Tech Advisor', 'role': 'Tech', 'status': 'active', 'price': 20},
        {'name': 'Delivery Expert', 'role': 'Logistics', 'status': 'active', 'price': 12},
        {'name': 'Warranty Specialist', 'role': 'Support', 'status': 'active', 'price': 18},
    ]
    agents = []
    for data in agents_data:
        agent = Agent(**data)
        db.add(agent)
        db.commit()
        agents.append(agent)
    print(f'✅ {len(agents)} agents created')
    
    # 2. Створюємо покупки (використовуємо price замість amount)
    for i in range(15):
        agent = random.choice(agents)
        purchase = Purchase(
            user_id=user.id,
            agent_id=agent.id,
            price=random.randint(50, 500),  # ← price, не amount!
            created_at=datetime.now() - timedelta(days=random.randint(0, 7))
        )
        db.add(purchase)
    db.commit()
    print('✅ 15 purchases created')
    
    # 3. Створюємо повідомлення
    intents = ['support', 'sales', 'tech', 'delivery', 'warranty', 'greeting']
    messages = [
        'Hello, I need help with my order',
        'When will my package arrive?',
        'I want to return an item',
        'Tell me about your products',
        'My device is not working',
        'Thanks for your support!',
        "I can't log in to my account",
        'Do you have a warranty?',
    ]
    responses = [
        'How can I help you?',
        'Let me check your order status',
        'Sure, I can help with returns',
        'Here are our latest products',
        'Let me troubleshoot that for you',
        "You're welcome!",
        'I can help reset your password',
        'Yes, we have a 2-year warranty',
    ]
    
    for i in range(30):
        msg = ChatMessage(
            user_id=user.id,
            agent_id=random.choice(agents).id,
            message=random.choice(messages),
            response=random.choice(responses),
            intent=random.choice(intents),
            status=random.choice(['ok', 'ok', 'ok', 'ok', 'ok', 'error']),
            response_time=round(random.uniform(0.3, 3.0), 1),
            created_at=datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
        )
        db.add(msg)
    db.commit()
    print('✅ 30 messages created')
    
    print('\n🎉 ALL TEST DATA ADDED!')
    print(f'📊 Users: {db.query(User).count()}')
    print(f'🤖 Agents: {db.query(Agent).count()}')
    print(f'💰 Purchases: {db.query(Purchase).count()}')
    print(f'💬 Messages: {db.query(ChatMessage).count()}')

if __name__ == "__main__":
    seed_dashboard()