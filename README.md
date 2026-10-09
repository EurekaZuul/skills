# EurekaZuul Skills（私有）

适用于 Claude Code、Codex 等支持 Agent Skills 的工具。

## 安装

需要 Node.js 22 及以上。在项目根目录执行，Skill 只装到当前项目，不会装到全局：

```bash
npx skills add EurekaZuul/skills --skill feishu-openapi -a claude-code codex -y
```

装好后，Skill 文件放在项目的 `.agents/skills/feishu-openapi/`（Codex 读这里），`.claude/skills/feishu-openapi` 是指向它的链接（Claude Code 读这里）。不要加 `-g`，加了会装到全局，所有项目都会加载。

仓库目前为私有，安装时需要有访问权限（本机 git 已登录 GitHub，或设置 `GITHUB_TOKEN`）。

## 目录

| Skill | 用途 |
| --- | --- |
| `feishu-openapi` | 用飞书自建应用的 App ID / App Secret 读写知识库和云文档 |

凭证一律通过环境变量提供（`FEISHU_APP_ID`、`FEISHU_APP_SECRET`），仓库中不保存任何真实凭证。
