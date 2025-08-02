import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()
api_key = os.getenv("CEREBRAS_API_KEY")
client = Cerebras(api_key=api_key)

def get_completion(prompt, model="llama3.1-8b", max_tokens=1024):
    chat_completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    return chat_completion.choices[0].message.content

# Test the client
if __name__ == "__main__":
    print(get_completion("Hello, world!"))