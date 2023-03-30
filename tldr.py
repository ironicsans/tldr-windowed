import sys
import openai
import os
from bs4 import BeautifulSoup
import requests
import time
import math
import tkinter as tk

# Set up API key
openai.api_key = "OPENAI_API_KEY"


def fetch_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f"Failed to fetch {url}: {e}")
        raise


def extract_main_text(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove irrelevant elements
    for element in soup.find_all(['header', 'footer', 'nav', 'aside']):
        element.decompose()

    text = soup.get_text(separator=" ")
    return text


def split_text(text, max_tokens=3000):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)

        if len(" ".join(current_chunk)) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def summarize(text):
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text for me: {text}"},
        ],
    )
    summary = result.choices[0].message.content
    return summary

def get_elapsed_time(initial_time):
    return math.floor((time.time() - initial_time))


def main():
    def summarize_url():
        url = url_entry.get()
        try:
            html = fetch_webpage(url)
            main_text = extract_main_text(html)
            text_chunks = split_text(main_text, 3000)

            summaries = []

            for count, chunk in enumerate(text_chunks):
                s = summarize(chunk)
                summaries.append(s)

            final_summary = summarize(' '.join(summaries))

            summary_text.delete('1.0', tk.END)
            summary_text.insert(tk.END, final_summary)
        
        except Exception as e:
            summary_text.delete('1.0', tk.END)
            summary_text.insert(tk.END, f"Error: {e}")

    # Create window
    window = tk.Tk()
    window.title("URL Summarizer")

    # Create URL entry
    url_label = tk.Label(window, text="Enter URL:")
    url_label.pack()
    url_entry = tk.Entry(window, width=50)
    url_entry.pack()

    # Create summarize button
    summarize_button = tk.Button(window, text="Summarize", command=summarize_url)
    summarize_button.pack()

    # Create summary text box
    summary_label = tk.Label(window, text="Summary:")
    summary_label.pack()
    summary_text = tk.Text(window, wrap=tk.WORD, width=80, height=20)
    summary_text.pack(fill=tk.BOTH, expand=True)

    window.mainloop()

if __name__ == "__main__":
    main()
