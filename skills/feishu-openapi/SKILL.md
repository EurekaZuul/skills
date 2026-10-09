---
name: feishu-openapi
description: 用飞书企业自建应用的 App ID / App Secret 读写飞书知识库（Wiki）和云文档（Docx）。当用户要求查看、新建、整理、修改或删除飞书知识库页面或文档，或要接入飞书 OpenAPI / 官方 MCP 时使用。
---

# 飞书知识库与文档操作

## 第一步：检查凭证
凭证只从环境变量读取：`FEISHU_APP_ID`、`FEISHU_APP_SECRET`。先检查两者是否已设置（只判断是否为空，**不要打印值**）。

下文的 `scripts/feishu.py` 指本 Skill 目录下的脚本（项目级安装时通常位于 `.claude/skills/feishu-openapi/scripts/feishu.py` 或 `.agents/skills/feishu-openapi/scripts/feishu.py`），请在项目根目录用该完整路径运行，这样脚本能读到项目根目录的 `.env`。

**已设置**：运行 `python3 <本 Skill 目录>/scripts/feishu.py check`，能列出知识空间就可以开始干活。

**未设置**：停下来，引导用户完成以下设置，完成后再运行 `check`：
1. 在 [飞书开发者后台](https://open.feishu.cn/app) 创建「企业自建应用」。
2. 在「权限管理」开通需要的权限（只读至少要知识库和云文档的查看权限；要新建、修改、删除再加编辑权限）。具体权限名查 `references/links.md` 里的「API 权限列表」。
3. 创建版本并发布，等管理员审批通过。未发布权限不生效。
4. 打开要操作的知识空间，「设置 → 成员设置」把应用加为成员（可编辑或管理员）。若搜不到应用，参考「知识库常见问题」：把应用机器人拉进一个群，再把群加为空间成员。
5. 在「凭证与基础信息」拿到 App ID 和 App Secret，**由用户自己**在本机设置环境变量，例如写进 `~/.zshrc` / `~/.bashrc`：
   ```
   export FEISHU_APP_ID=cli_xxx
   export FEISHU_APP_SECRET=xxx
   ```
   或写进项目根目录的 `.env` 并确认 `.env` 已在 `.gitignore` 里。
   不要让用户把 Secret 发在对话里，也不要替用户把 Secret 写进任何会被提交的文件。

`check` 返回空列表时，通常是应用版本未发布，或应用没被加为空间成员（只在单篇文档上加协作者，只能看到那一篇及其子页面）。

## 第二步：操作
`scripts/feishu.py`（仅依赖 Python 3 标准库，会自动读取当前目录的 `.env`）提供：
- `check` / `spaces`：验证凭证并列出可访问的知识空间
- `tree <space_id>`：打印目录树
- `node <wiki链接或token>`：查看节点信息
- `read <wiki链接或token>`：读取文档纯文本
- `create <space_id> <标题> [--parent <node>] [--file 内容.md]`：新建文档，可从简单 Markdown 写入内容

更复杂的需求（移动、改标题、删除、多维表格、消息等）去 `references/links.md` 查官方文档自己实现。也可以接入飞书官方 MCP：
`npx -y @larksuiteoapi/lark-mcp mcp -a "$FEISHU_APP_ID" -s "$FEISHU_APP_SECRET" -l zh`

## 规则
- 删除、批量修改前先列出影响范围，经用户确认再执行；删除不可撤回。
- 应用身份不能新建「知识空间」（需要 user_access_token）；请用户手动建空间并把应用加为成员。
- 遇到不熟悉的接口、参数、权限或错误码，查 `references/links.md` 里的官方文档，不要凭记忆猜。
- token 约 2 小时过期，报 99991663 时重新获取。
