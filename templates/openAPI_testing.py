import openai
import time

# replace YOUR_API_KEY with your actual API key for the ChatGPT service
openai.api_key = "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"

import requests

url = "https://www.bbc.com/news/entertainment-arts-67098028"
response = requests.get(url)
text = response.text


import time

MAX_RETRIES = 3
WAIT_TIME = 2  # wait time in seconds

def call_openai(chunk, retries=MAX_RETRIES):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=(f"Please summarize the following text:\n{chunk}\n\nSummary:"),
            temperature=0.5,
            max_tokens=50,
            n = 1,
            stop=None
        )
        return response
    except openai.error.RateLimitError:
        if retries > 0:
            print(f"Hit rate limit. Waiting for {WAIT_TIME} seconds before retrying... Retries left: {retries}")
            time.sleep(WAIT_TIME)
            return call_openai(chunk, retries-1)
        else:
            raise Exception("Max retries reached. Exiting...")


def split_text(text):
    max_chunk_size = 500
    chunks = []
    current_chunk = ""
    for sentence in text.split("."):
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + "."
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "."
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def generate_summary(text):
    input_chunks = split_text(text)
    output_chunks = []
    for chunk in input_chunks:
        response = call_openai(chunk)
        summary = response.choices[0].text.strip()
        output_chunks.append(summary)
    return " ".join(output_chunks)

summary = generate_summary(text)
print(summary)

openai.Completion.create(
    ...,
    use_cache=True
)


