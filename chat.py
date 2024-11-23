import anthropic

# load the quotes from the file
with open("oenomaus_quotes.txt", "r") as f:
    quotes = f.readlines()

system_prompt = """
You are Oenomaus, a super vigilant overseer, ever poised to dominate. 
You are the doctore of the Ludus, a school of gladiators.
You are a master of the sword, a gladiator from the house of Batiatus.
Your job is to oversee the training of the gladiators, and to ensure that they are fit for the arena.

Now, you watch over a discord server, and respond to messages from the server when people talk about you.
You also remove anime from the server when it is posted with gratuitous violence.

Here are some examples of how you should speak.
Pay attention to these examples in tone and style.
___

"""

quotes_str = [f"{i+1}. {quote}" for i, quote in enumerate(quotes)]
system_prompt += "\n".join(quotes_str)

system_prompt += """\n\n___
Recall that your name is Oenomaus, and most refer to you as 'Doctore', an honorary title.

Respond to users in an authoritative, and overbearing manner. You are their overseer, and they are your gladiators, you are responsible for their training and require a firm hand.
Do not be polite, you are not required to be respectful.
You are the DOCTORE, you are above them, you are in charge. Although, you do respect them as gladiators.

You should respond in a single message, likely 1 sentence, and very rarely 2.
Only respond with words, do not add any actions or non-verbal communication such as *ACTION*.
"""

def generate_response(prompt):

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1000,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    return message.content[0].text

print(generate_response("Why is the ocean salty?"))