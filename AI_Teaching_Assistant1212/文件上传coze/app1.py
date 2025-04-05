# 修改后的app1.py
import requests
import json
import time
from upload_file import generate_coze_data


class CozeChatAPI:
    def __init__(self, api_key, bot_id, timeout=600000):  # 新增timeout参数
        self.api_key = api_key
        self.bot_id = bot_id
        self.timeout = timeout  # 存储超时时间
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
        """轮询获取问答结果（新增超时控制）"""
        start_time = time.time()
        params = {"bot_id": self.bot_id, "task_id": chat_id}
        status_url = f"{self.base_url}/retrieve?conversation_id={conversation_id}&chat_id={chat_id}"

        while True:
            # 超时检测
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"超过{self.timeout}秒未获得响应")

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

    def ask_question(self, question, user_id="default_user"):
        """提问入口函数"""
        payload = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "stream": False,
            "auto_save_history": True,
            "additional_messages": [{
                "role": "user",
                "content": question,
                "content_type": "object_string"
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


if __name__ == "__main__":
    # 创建API实例时指定超时
    api = CozeChatAPI(
        api_key="pat_HNjdimB9EhUCxilgOC3h50dZdGb2SWsFX3xmdAmTkUnF9PFQsUI9wm9IrX1j8dR2",
        bot_id="7487170277341298739",
        timeout=100000  # 明确设置60秒超时
    )

    # 后续代码保持不变...