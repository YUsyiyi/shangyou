# app1.py
import requests
import json
import time


class CozeChatAPI:
    def __init__(self, api_key, bot_id):
        self.api_key = api_key
        self.bot_id = bot_id
        self.base_url = 'https://api.coze.cn/v3/chat'
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }

    def _process_question_answer(self, response_data):
        """处理问答响应"""
        results = {
            'answers': [],
            'follow_ups': []
        }

        if response_data.get('code'):
            return {"error": response_data['msg']}

        for item in response_data['data']:
            if item['type'] == 'answer':
                results['answers'].append(item['content'])
            elif item['type'] == 'follow_up':
                results['follow_ups'].append(item['content'])

        return results

    def _get_question_answer(self, conversation_id, chat_id):
        """轮询获取问答结果"""
        params = {"bot_id": self.bot_id, "task_id": chat_id}
        status_url = f"{self.base_url}/retrieve?conversation_id={conversation_id}&chat_id={chat_id}"

        while True:
            try:
                response = requests.get(status_url, headers=self.headers)
                response.raise_for_status()
                response_data = response.json()

                if response_data['data']['status'] == 'completed':
                    answer_url = f"{self.base_url}/message/list?chat_id={chat_id}&conversation_id={conversation_id}"
                    response = requests.get(answer_url, headers=self.headers, params=params)
                    response.raise_for_status()
                    return self._process_question_answer(response.json())

                time.sleep(1)
            except Exception as e:
                return {"error": str(e)}

    def ask_question(self, question_text, user_id="default_user"):
        """提问入口函数"""
        payload = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "stream": False,
            "auto_save_history": True,
            "additional_messages": [{
                "role": "user",
                "content": question_text,
                "content_type": "text"
            }]
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            response_data = response.json()

            chat_id = response_data['data']['id']
            conversation_id = response_data['data']['conversation_id']
            return self._get_question_answer(conversation_id, chat_id)

        except Exception as e:
            return {"error": str(e)}


# API配置常量
API_KEY ="pat_YIYDDe70PzCmnZrK30PhZI2HND1xBanYMc2hdhEFDyQvskVvHTc4mIxPv3h06H3P"
BOT_ID = "7487530164101120009"

def init_coze_client():
    """初始化并返回Coze客户端实例"""
    return CozeChatAPI(api_key=API_KEY, bot_id=BOT_ID)

def get_coze_response(question):
    """获取Coze API响应"""
    api = init_coze_client()
    result=api.ask_question(question)
    return result
import streamlit as st
def display_response(question):
    """显示API响应结果"""
    result=get_coze_response(question)
    if 'error' in result:
        answers_str = f"出错: {result['error']}"
        st.error(answers_str)
        st.error(result)
    else:
        for answer in result['answers']:
           st.write(answer)
# # 保留原有直接执行功能
# if __name__ == "__main__":
#     result = get_coze_response("明天天气怎么样")
#     print(result)
