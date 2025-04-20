import json

def get_coze_parameters():
    """从output.json文件中读取参数"""
    try:
        with open("output.json", "r") as f:
            data = json.load(f)
            return data["file_id"], data["user_text"]
    except FileNotFoundError:
        print("错误：未找到output.json文件，请先运行Streamlit应用并提交数据")
        return None, None
    except KeyError as e:
        print(f"错误：文件格式不正确，缺少键 {e}")
        return None, None
    except json.JSONDecodeError:
        print("错误：文件内容解析失败，请检查文件格式")
        return None, None

def generate_coze_data():
    """生成要发送的JSON数据"""
    b, user_text = get_coze_parameters()
    if not all([b, user_text]):
        return None
    data = [
        {"type": "text", "text": user_text},
        {"type": "file", "file_id": b}
    ]#####修改点
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)

if __name__ == "__main__":
    print(generate_coze_data())  # 测试用

