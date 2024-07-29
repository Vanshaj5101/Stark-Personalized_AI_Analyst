def get_bot_user_id():
    try:
        slack_client = WebClient(token=SLACK_BOT_TOKEN)
        response = slack_client.auth_test()
        print(response)
        return response["user_id"]
    except SlackApiError as e:
        print("Error Occured: {e}")
    