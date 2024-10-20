import os
from openai import OpenAI


client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "do you know a mad girl aforza?"
        }
    ]
)

print(completion.choices[0].message)