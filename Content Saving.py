import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# buffer 用于记录当前对话的状态
# 结构: { "指纹(用户提问)": {"filename": "...", "length": 123, "ai_response": "..."} }
chat_buffer = {}

@app.route('/save_chat', methods=['POST'])
def save_chat():
    data = request.json
    user_prompt = data.get('user_prompt', '')
    ai_response = data.get('ai_response', '')
    source = data.get('source', 'unknown')

    if not user_prompt or not ai_response:
        return jsonify({"status": "ignored", "reason": "empty content"}), 200

    fingerprint = user_prompt[:20] if len(user_prompt) > 20 else user_prompt

    #data文件夹地址获取
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(base_dir, "data")

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    current_length = len(ai_response)
    is_update_needed = False

    #新json的生成与AI打字机式输出导致的新json覆盖旧json机制
    if fingerprint not in chat_buffer:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{current_time}_{source}.json"
        
        chat_buffer[fingerprint] = {
            "filename": filename,
            "length": current_length,
            "ai_response": ai_response
        }
        is_update_needed = True
    else:
        if current_length > chat_buffer[fingerprint]["length"]:
            chat_buffer[fingerprint]["length"] = current_length
            chat_buffer[fingerprint]["ai_response"] = ai_response
            is_update_needed = True
        elif current_length == chat_buffer[fingerprint]["length"]:
            return jsonify({"status": "ignored", "reason": "length unchanged, loop stopped"}), 200

    #写入json文件
    if is_update_needed:
        current_file = chat_buffer[fingerprint]["filename"]
        file_path = os.path.join(target_folder, current_file)

        json_data = {
            "source": source,
            "record_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "user_fingerprint": user_prompt,
            "ai_response": chat_buffer[fingerprint]["ai_response"],
            "content_length": chat_buffer[fingerprint]["length"]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        print(f"数据已同步至 JSON: {current_file} (当前AI文本长度: {current_length})")

    return jsonify({"status": "saved", "file": chat_buffer[fingerprint]["filename"]}), 200

if __name__ == "__main__":
    print("AI记录服务器启动中 (JSON模式)...")
    app.run(port=5000, debug=True)
