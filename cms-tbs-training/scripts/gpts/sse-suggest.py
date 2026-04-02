#!/usr/bin/env python3
"""
gpts / sse-suggest 脚本

用途：SSE核心接口，用于训战对话交互

使用方式：
  # 开始训练
  python scripts/gpts/sse-suggest.py start_training <sessionId> <appId> <sceneId> [sourceId] [cloudCategoryId] [trainingType] [mode]

  # 提交对话
  python scripts/gpts/sse-suggest.py submit_dialogue <sessionId> <appId> <content> <trainingRecordId> <round> [type]

  # 生成AI点评
  python scripts/gpts/sse-suggest.py generate_ai_comment <sessionId> <appId> <trainingRecordId>

  # 下一关
  python scripts/gpts/sse-suggest.py next_level <sessionId> <appId> <trainingRecordId>

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）
  XG_CORP_ID     — corpId（必须；由 cms-auth-skills 预先准备）
  XG_EMPLOYEE_ID — employeeId（必须；由 cms-auth-skills 预先准备）
  XG_PERSON_ID   — personId（必须；由 cms-auth-skills 预先准备）

参数：
  sessionId        - 会话ID（必填）
  appId            - 应用ID（必填）
  action           - 动作：start_training/submit_dialogue/generate_ai_comment/next_level
  content          - 用户输入内容
  trainingRecordId - 训练记录ID（submit_dialogue/generate_ai_comment/next_level时必填）
  round            - 轮次（submit_dialogue时必填）
  type             - 类型：user/coach（submit_dialogue时必填，默认user）
  sceneId          - 场景ID（start_training时必填）
  sourceId         - 来源ID（start_training时可选，默认58）
  cloudCategoryId  - 云分类ID（start_training时可选，默认124）
  trainingType     - 训练类型：practice/battle（start_training时可选，默认practice）
  mode             - 模式：true/false（start_training时可选，true=练习，false=训战，默认true）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/gpts/sse-suggest.md 中声明的一致）
BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn"
API_URL = f"{BASE_URL}/gpts/sseClient/ai/suggest"

# 固定的 Headers
FIXED_HEADERS = {
    "accept": "text/event-stream",
    "appkey": "WtEkxhUvmHhiE4wjaYTaVcHWKiYTiLJ8",
    "content-type": "application/json"
}


def build_headers() -> dict:
    """构建请求头"""
    headers = dict(FIXED_HEADERS)
    token = os.environ.get("XG_USER_TOKEN")
    corp_id = os.environ.get("XG_CORP_ID")
    employee_id = os.environ.get("XG_EMPLOYEE_ID")
    person_id = os.environ.get("XG_PERSON_ID")

    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    if not corp_id:
        print("错误: 请设置环境变量 XG_CORP_ID", file=sys.stderr)
        sys.exit(1)
    if not employee_id:
        print("错误: 请设置环境变量 XG_EMPLOYEE_ID", file=sys.stderr)
        sys.exit(1)
    if not person_id:
        print("错误: 请设置环境变量 XG_PERSON_ID", file=sys.stderr)
        sys.exit(1)

    headers["access-token"] = token
    headers["corpid"] = corp_id
    headers["employeeid"] = employee_id
    headers["personid"] = person_id

    return headers


def call_sse(action: str, session_id: str, app_id: str,
             content: str = None,
             training_record_id: str = None,
             round_val: int = None,
             type_val: str = None,
             scene_id: str = None,
             source_id: int = None,
             cloud_category_id: str = None,
             training_type: str = None,
             mode: bool = None) -> list:
    """调用SSE接口，返回事件列表"""

    if not session_id or not app_id:
        print("错误: sessionId, appId 为必填参数", file=sys.stderr)
        sys.exit(1)

    # 构建 extMap
    ext_map = {"action": action}

    if action == "start_training":
        if not scene_id:
            print("错误: start_training 需要 sceneId 参数", file=sys.stderr)
            sys.exit(1)
        ext_map["sceneId"] = scene_id
        ext_map["doctorId"] = None  # 必须是 null
        ext_map["sourceId"] = source_id if source_id is not None else 58  # 必须是数字
        ext_map["cloudCategoryId"] = cloud_category_id or "124"
        ext_map["trainingType"] = training_type or "practice"
        ext_map["mode"] = mode if mode is not None else True
        content = content or "进入训练"

    elif action in ("submit_dialogue", "generate_ai_comment", "next_level"):
        if not training_record_id:
            print(f"错误: {action} 需要 trainingRecordId 参数", file=sys.stderr)
            sys.exit(1)
        ext_map["trainingRecordId"] = training_record_id
        if action == "submit_dialogue":
            ext_map["round"] = round_val if round_val is not None else 1
            ext_map["type"] = type_val or "user"
            if not content:
                print("错误: submit_dialogue 需要 content 参数", file=sys.stderr)
                sys.exit(1)
        elif action == "generate_ai_comment":
            content = content or "生成AI点评"  # 必须是 "生成AI点评"，不能为空
        else:
            content = content or "下一关"

    # 构建 Body
    body = {
        "sessionId": session_id,
        "content": content,
        "extMap": ext_map,
        "msgList": [],
        "appId": app_id
    }

    headers = build_headers()
    req_body = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(API_URL, data=req_body, headers=headers, method="POST")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    events = []
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            for line in resp:
                line = line.decode('utf-8', errors='replace').strip()
                if line.startswith('event:'):
                    event_type = line[6:].strip()
                    events.append({"type": "event", "data": event_type})
                elif line.startswith('data:'):
                    data = line[5:].strip()
                    if data:
                        try:
                            events.append({"type": "data", "data": json.loads(data)})
                        except:
                            events.append({"type": "data", "data": data})
    except urllib.error.URLError as e:
        if hasattr(e, 'read'):
            print(f"错误: {e.read().decode('utf-8')}", file=sys.stderr)
        else:
            print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    return events


def main():
    if len(sys.argv) < 4:
        print("错误: 参数不足", file=sys.stderr)
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]
    session_id = sys.argv[2]
    app_id = sys.argv[3]

    events = []

    if action == "start_training":
        scene_id = sys.argv[4] if len(sys.argv) > 4 else None
        source_id = int(sys.argv[5]) if len(sys.argv) > 5 else 58
        cloud_category_id = sys.argv[6] if len(sys.argv) > 6 else "124"
        training_type = sys.argv[7] if len(sys.argv) > 7 else "practice"
        mode = sys.argv[8].lower() == "true" if len(sys.argv) > 8 else True
        events = call_sse(action, session_id, app_id, scene_id=scene_id,
                         source_id=source_id, cloud_category_id=cloud_category_id,
                         training_type=training_type, mode=mode)

    elif action == "submit_dialogue":
        if len(sys.argv) < 6:
            print("错误: submit_dialogue 需要 content 和 trainingRecordId", file=sys.stderr)
            sys.exit(1)
        content = sys.argv[4]
        training_record_id = sys.argv[5]
        round_val = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        type_val = sys.argv[7] if len(sys.argv) > 7 else "user"
        events = call_sse(action, session_id, app_id, content=content,
                         training_record_id=training_record_id, round_val=round_val, type_val=type_val)

    elif action == "generate_ai_comment":
        if len(sys.argv) < 5:
            print("错误: generate_ai_comment 需要 trainingRecordId", file=sys.stderr)
            sys.exit(1)
        training_record_id = sys.argv[4]
        events = call_sse(action, session_id, app_id, training_record_id=training_record_id)

    elif action == "next_level":
        if len(sys.argv) < 5:
            print("错误: next_level 需要 trainingRecordId", file=sys.stderr)
            sys.exit(1)
        training_record_id = sys.argv[4]
        events = call_sse(action, session_id, app_id, training_record_id=training_record_id)

    else:
        print(f"错误: 未知 action '{action}'", file=sys.stderr)
        sys.exit(1)

    # 输出结果
    for event in events:
        if event["type"] == "event":
            print(f"\n--- Event: {event['data']} ---")
        else:
            print(json.dumps(event["data"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
