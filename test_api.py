from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Reply with exactly: 'WSL Python API works'"}]
)
print(msg.content[0].text)
