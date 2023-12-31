# Frontend code
# 의존성은 config.py하고 conf.json밖에 없어서 별도의 프로젝트에서 혼자 돌려도 됨
import datetime
import ssl
import asyncio
import logging
import os
import subprocess
from threading import Event
import requests
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from config import conf
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 여기 코드 한 두줄 추가할듯?
# HOSTNAME = os.uname().nodename
BOT_TOKEN = conf['bot_token']
SOCKET_TOKEN = conf['bot_socket']
BOTNAME = 'bot'

# Slack 고유의 userId로 들어옴
ALLOW_USERS = ['U05LHSC5VA8']

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.WARN)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

SLACK_CLIENT = SocketModeClient(
    # This app-level token will be used only for establishing a connection
    app_token=SOCKET_TOKEN,  # xapp-A111-222-xyz
    # You will be using this AsyncWebClient for performing Web API calls in listeners
    web_client=WebClient(token=BOT_TOKEN, ssl=ssl_context)  # xoxb-111-222-xyz
)

class SlackMessage:
    # 메시지 처리를 위한 부분
    def __init__(self, script, option, username, userid, slackch, slackts):
        self.script = script
        self.option = option
        self.username = username
        self.userid = userid
        self.channel = slackch
        self.timestamp = slackts

    @classmethod
    def CheckUserAuthentication(cls, slack_text, slack_userid, slack_channel, slack_timestamp, slack_presentts = None):
        if slack_presentts and slack_presentts != 'None':
        # if slack_presentts and slack_presentts != None:    
            slackts = slack_presentts
        else:
            slackts = slack_timestamp
        if 'user' not in ALLOW_USERS:
            return None 
        date_time = datetime.fromtimestamp(float(slackts))
        access_result = request.post('https://localhost/access',data ={
            'user_id':slack_userid,
            'channel_id':slack_channel,
            'access_time':date_time.strftime('%Y-%m-%d %H:%M:%S')
        },verify=False).json()
        access_id=''
        if(access_result)['result'== True]:
            access_id = access_result['access_id']
        else:
            return None # or error print code

        username = slack_userid
        user_message = slack_text.split(' ', 1)
        return cls(user_message, username, slack_userid, slack_channel, slackts)

    def task_run(self):
        try:
            # API 호출
            pass
            # 결과 회신 프로세스
        except Exception as task_run_e:
            run_result = str(task_run_e)
            logging.warning('task_run_error func: %s', run_result)
        requests.post('https://slack.com/api/chat.postMessage', {
                'token': BOT_TOKEN,
                'channel': self.channel,
                'text': run_result,
                'thread_ts': self.timestamp,
                'unfurl_links': False
            }, verify=False)

async def Bot(text, userid, slackch, slackts, presentts = None):
    try:
        slack_bot = SlackMessage.CheckUserAuthentication(text, userid, slackch, slackts, presentts)
        if not slack_bot:
            return
        slack_bot.task_run()
    except Exception as CommandBot_e:
        CommandBot_error = str(CommandBot_e)
        logging.warning('CommandBot func: %s', CommandBot_error)
# 같이 처리를 해보자..
def is_bot_call(slack_orignal_msg, slack_orignal_channel):
    """
    Check if the message is a bot call
    """
    pass

def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api":
        # Acknowledge the request anyway (구조체 많음..)
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)
        if req.payload["event"]["type"] == "message":
            slack_subtype = req.payload["event"].get("subtype")
            if slack_subtype is None:
                userid = req.payload["event"]['user']
                slack_text = req.payload["event"]['text'].lower()
                channel_id = req.payload["event"]['channel']
                present_ts = ''
                thread_ts = req.payload["event"]['ts']
                if 'thread_ts' in req.payload["event"]:
                    present_ts = req.payload["event"]['thread_ts']
                asyncio.run(Bot(slack_text, userid, channel_id, str(thread_ts), str(present_ts)))

if __name__ == "__main__":
    try:
        #rtm.start()
        # Add a new listener to receive messages from Slack
        # You can add more listeners like this
        SLACK_CLIENT.socket_mode_request_listeners.append(process)
        # Establish a WebSocket connection to the Socket Mode servers
        SLACK_CLIENT.connect()
        # Just not to stop this process
        Event().wait()
    except Exception as main_e:
        error = str(main_e)
        logging.warning('main func: %s', error)