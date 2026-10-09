# EurekaZuul Skills（私有）

适用于 Claude Code、Codex 等支持 Agent Skills 的工具。

## 安装

需要 Node.js 22 及以上。向仓库管理员申请授权码（只读令牌），然后执行：

```bash
GITHUB_TOKEN=<授权码> npx skills add EurekaZuul/skills --skill feishu-openapi
```

已有本仓库访问权限的 GitHub 用户可直接执行 `npx skills add EurekaZuul/skills`。

## 目录

| Skill | 用途 |
| --- | --- |
| `feishu-openapi` | 用飞书自建应用的 App ID / App Secret 读写知识库和云文档 |

凭证一律通过环境变量提供（`FEISHU_APP_ID`、`FEISHU_APP_SECRET`），仓库中不保存任何真实凭证。
