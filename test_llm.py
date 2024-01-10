from ez_manim import OpenAIManim

llm = OpenAIManim()

query = "create a square of size 2 in the middle"
messages = llm.get_windowed_history()
messages.append({"role": "user", "content": query})

response = llm.generate(messages)

print(response)

llm.add_to_history("user", query)
llm.add_to_history("assistant", response)

print(llm.get_windowed_history())
