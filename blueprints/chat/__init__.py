from flask import Blueprint, render_template, request, Response
from lib import DEFAULT_SYSTEM_PROMPT
import openai
import json

chat = Blueprint("chat", __name__, template_folder="templates/")


@chat.route("/")
def index():
    return render_template("chat/index.html", systemPrompt=DEFAULT_SYSTEM_PROMPT)


@chat.post("/complete")
def complete():
    rJson = request.json
    systemPrompt = rJson["systemPrompt"]
    userPrompt = rJson["userPrompt"]
    conversation = rJson["messages"]
    resp = Response(
        json.dumps(getCompletion(systemPrompt, json.loads(conversation), userPrompt)),
        mimetype="application/json"
    )
    return resp


def getCompletion(systemPrompt: str, conversation: list[str], userPrompt: str):
    messages = [
        {"role": "system", "content": systemPrompt},
    ]
    for message in conversation:
        messages.append(message)
    messages.append({"role": "user", "content": userPrompt})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
    )
    # Need to parse a bit
    return response['choices'][0]['message']
