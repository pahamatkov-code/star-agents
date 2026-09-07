"""
AGENTS_REGISTRY — централізований реєстр усіх AI‑агентів.
Кожен агент створюється через фабричну функцію create_*_agent(),
що дозволяє легко додавати нових агентів у майбутньому.
"""

from typing import Optional
from app.agents.ecommerce_support_agent import create_ecommerce_support_agent
# У майбутньому тут можна додати:
# from app.agents.seo_agent import create_seo_agent
# from app.agents.marketing_agent import create_marketing_agent
# from app.agents.analytics_agent import create_analytics_agent

AGENTS_REGISTRY = {
    "ecommerce_support": create_ecommerce_support_agent(),
    # "seo": create_seo_agent(),
    # "marketing": create_marketing_agent(),
    # "analytics": create_analytics_agent(),
}

def get_agent(agent_name: str) -> Optional[object]:
    """
    Повертає інстанс агента за його ім'ям.
    Якщо агент не знайдений — повертає None.
    """
    return AGENTS_REGISTRY.get(agent_name)
