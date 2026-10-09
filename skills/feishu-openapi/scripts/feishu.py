#!/usr/bin/env python3
"""Minimal Feishu wiki/docx helper. Reads FEISHU_APP_ID / FEISHU_APP_SECRET from env (or ./.env). Python 3 stdlib only."""
import json, os, re, sys, urllib.request, urllib.error

BASE = os.environ.get("FEISHU_BASE_URL", "https://open.feishu.cn/open-apis")
TOKEN = None
SETUP_HINT = ("未找到 FEISHU_APP_ID / FEISHU_APP_SECRET。\n"
              "请在飞书开发者后台创建企业自建应用、开通权限并发布，把应用加为知识空间成员，"
              "然后在本机设置这两个环境变量（或写进已加入 .gitignore 的 .env）后重试。详见 SKILL.md。")

def load_dotenv():
    if os.path.exists(".env"):
        for line in open(".env", encoding="utf-8"):
            m = re.match(r"\s*(?:export\s+)?(FEISHU_[A-Z_]+)\s*=\s*['\"]?([^'\"\n]*)", line)
            if m and not os.environ.get(m.group(1)):
                os.environ[m.group(1)] = m.group(2).strip()

def _req(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        return json.load(urllib.request.urlopen(r))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read() or b"{}")
        except ValueError:
            return {"code": e.code, "msg": str(e)}

def get_token():
    load_dotenv()
    aid, sec = os.environ.get("FEISHU_APP_ID"), os.environ.get("FEISHU_APP_SECRET")
    if not aid or not sec:
        sys.exit(SETUP_HINT)
    d = _req("POST", "/auth/v3/tenant_access_token/internal", {"app_id": aid, "app_secret": sec})
    if d.get("code"):
        sys.exit(f"获取 token 失败: {d.get('code')} {d.get('msg')}（检查 App ID / Secret 是否正确）")
    return d["tenant_access_token"]

def api(method, path, body=None):
    d = _req(method, path, body, TOKEN)
    if d.get("code"):
        sys.exit(f"{method} {path} 失败: {d.get('code')} {d.get('msg')}")
    return d.get("data", {})

def paged(path):
    pt = ""
    while True:
        sep = "&" if "?" in path else "?"
        d = api("GET", f"{path}{sep}page_size=50" + (f"&page_token={pt}" if pt else ""))
        yield from (d.get("items") or [])
        if not d.get("has_more"):
            return
        pt = d.get("page_token", "")

def node_token(s):
    m = re.search(r"/wiki/([A-Za-z0-9]+)", s)
    return m.group(1) if m else s

def get_node(s):
    return api("GET", f"/wiki/v2/spaces/get_node?token={node_token(s)}")["node"]

def tree(space, parent="", depth=0):
    q = f"/wiki/v2/spaces/{space}/nodes" + (f"?parent_node_token={parent}" if parent else "")
    for n in paged(q):
        print("  " * depth + f"- {n['title'] or '(无标题)'} [{n['obj_type']}] node={n['node_token']}")
        if n.get("has_child"):
            tree(space, n["node_token"], depth + 1)

def md_blocks(text):
    """Small markdown subset: #/##/### headings, - bullets, 1. ordered, plain paragraphs."""
    rules = [(r"^### (.*)", 5, "heading3"), (r"^## (.*)", 4, "heading2"), (r"^# (.*)", 3, "heading1"),
             (r"^\s*[-*] (.*)", 12, "bullet"), (r"^\s*\d+\. (.*)", 13, "ordered")]
    out = []
    for line in text.splitlines():
        s = line.rstrip()
        if not s.strip():
            continue
        bt, key, content = 2, "text", s
        for pat, b, k in rules:
            m = re.match(pat, s)
            if m:
                bt, key, content = b, k, m.group(1)
                break
        out.append({"block_type": bt, key: {"elements": [{"text_run": {"content": content}}]}})
    return out

def append(doc, blocks):
    for i in range(0, len(blocks), 50):
        api("POST", f"/docx/v1/documents/{doc}/blocks/{doc}/children", {"children": blocks[i:i + 50]})

USAGE = "用法: check | spaces | tree <space_id> | node <链接|token> | read <链接|token> | create <space_id> <标题> [--parent node] [--file x.md]"

def main(argv):
    global TOKEN
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(USAGE)
    TOKEN = get_token()
    cmd, args = argv[0], argv[1:]
    if cmd in ("check", "spaces"):
        items = list(paged("/wiki/v2/spaces"))
        if cmd == "check":
            print("凭证有效。")
        if not items:
            print("没有可访问的知识空间：确认应用版本已发布，且应用已加为空间成员。")
        for s in items:
            print(f"{s['name']}  space_id={s['space_id']}  {s.get('description', '')}")
    elif cmd == "tree":
        tree(args[0])
    elif cmd == "node":
        print(json.dumps(get_node(args[0]), ensure_ascii=False, indent=2))
    elif cmd == "read":
        n = get_node(args[0])
        if n["obj_type"] != "docx":
            sys.exit(f"该节点类型为 {n['obj_type']}，read 仅支持 docx")
        print(api("GET", f"/docx/v1/documents/{n['obj_token']}/raw_content")["content"])
    elif cmd == "create":
        space, title = args[0], args[1]
        body = {"obj_type": "docx", "node_type": "origin", "title": title}
        if "--parent" in args:
            body["parent_node_token"] = node_token(args[args.index("--parent") + 1])
        n = api("POST", f"/wiki/v2/spaces/{space}/nodes", body)["node"]
        if "--file" in args:
            append(n["obj_token"], md_blocks(open(args[args.index("--file") + 1], encoding="utf-8").read()))
        print(json.dumps({"node_token": n["node_token"], "obj_token": n["obj_token"]}))
    else:
        sys.exit(f"未知命令: {cmd}\n{USAGE}")

if __name__ == "__main__":
    main(sys.argv[1:])
