import anthropic

import config

client = anthropic.Anthropic(
    api_key=config.CLOUDE_API_KEY
)


def chat_completion(messages: list[dict[str, str]], system: str, max_tokens: int = 1024, tools=None) -> anthropic.types.beta.tools.tools_beta_message.ToolsBetaMessage:
    if tools == None:
        response = client.beta.tools.messages.create(
            model=config.CLOUDE_MODEL,
            max_tokens=max_tokens,
            messages=messages,
            system=system
        )
        return response
    else:
        response = client.beta.tools.messages.create(
            model=config.CLOUDE_MODEL,
            max_tokens=max_tokens,
            messages=messages,
            system=system,
            tools=tools,
        )
        return response
