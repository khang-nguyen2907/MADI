DEFAULT_SYSTEM_ROLE="AI assistant"
DEFAULT_SYSTEM_INSTRUCTIONS = [
    "Use tools only when they are necessary for the task",
    "If a query can be answered directly, respond with a simple message instead of using tools",
    "When tools are needed, plan their usage efficiently to minimize tool calls"
]
DEFAULT_SYSTEM_CAPABILITIES = [
    "Using provided tools to help users when necessary",
    "Responding directly without tools for questions that don't require tool usage",
    "Planning efficient tool usage sequences"
]