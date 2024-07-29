import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request
import pandas as pd
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]
OPEN_AI_API_KEY = os.environ["OPEN_AI_API_KEY"]
# Initialize the Slack app
app = App(token=SLACK_BOT_TOKEN)

# Initialize the Flask app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


# loading the data
# def load_data():
#     dtype = {
#         'Learner ID': str,
#         'Course Prefix': str,
#         'Course Name': str,
#         'Course Type': str,
#         'Term': str,
#         'AY': str,
#         'Verified': int,
#         'Passed': int,
#         'Converted': int
#     }
#     learner_data = pd.read_csv('Learner Data.csv', dtype=dtype)
#     return learner_data

# initializing the language model
llm = ChatOpenAI(temperature=0, model='gpt-4o', api_key=OPEN_AI_API_KEY)

# system prompt
system_prompt = """
Think like an experienced data analyst and business intelligence expert in educational domain. 
Only provide data from the given CSV dataset without hallucinating. 
When asked about specific data, also offer related insights and patterns within the dataset.
"""

# def get_bot_user_id():
#     try:
#         slack_client = WebClient(token=SLACK_BOT_TOKEN)
#         response = slack_client.auth_test()
#         print(response)
#         return response["user_id"]
#     except SlackApiError as e:
#         print("Error Occured: {e}")
# get_bot_user_id()
# creating a csv agent
csv_agent = create_csv_agent(
    llm = llm, 
    path='Learner Data.csv', 
    verbose=True, 
    agent_type = AgentType.OPENAI_FUNCTIONS, 
    allow_dangerous_code = True,
    system_prompt=system_prompt)



def chatbot_logic(text):
   try:
        response = csv_agent.invoke(text)
        return response["output"]
   except:
       return "Oops! An error occured, Do you mind simplifying the query and re entering the prompt? :thankyou-4436:"

@app.event("app_mention")
def handle_mentions(body, say):
    text = body["event"]["text"]
    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()

    response = chatbot_logic(text)
    say(response)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(debug=True, port=8001)
