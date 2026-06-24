from app.agents.ecommerce_support_agent import create_ecommerce_support_agent

AGENTS_REGISTRY = {
    "ecommerce_support": create_ecommerce_support_agent,
}
