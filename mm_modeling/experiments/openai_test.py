from openai import OpenAI
import os
# TODO: get openAI api key

client = OpenAI(
  api_key=...
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);

