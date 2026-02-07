# 项目记忆 - 豆包语音服务 Skills

## 项目概述

ByteDance 火山引擎豆包语音服务的 Claude Code Skills 封装，包含 TTS 语音合成和 ASR 语音识别两个 Skill。

## 目录结构

```
doubao-skills/
├── skills/
│   ├── doubao-tts/          # TTS 语音合成 Skill
│   │   ├── SKILL.md         # Skill 定义（英文 + 中文意图关键词）
│   │   ├── VOICES.md        # 音色参考文档
│   │   └── scripts/tts.py   # TTS 执行脚本
│   └── doubao-asr/          # ASR 语音识别 Skill
│       ├── SKILL.md         # Skill 定义（英文 + 中文意图关键词）
│       ├── WORKFLOW.md      # 工作流配置参考
│       └── scripts/asr.py   # ASR 执行脚本
├── scripts/
│   └── install-openclaw.sh  # 一键安装脚本
├── .claude-plugin/          # Claude Code 插件配置
├── docs/                    # 架构和规范文档
├── README.md                # 项目文档（中文）
├── CHANGELOG.md             # 版本记录
└── LICENSE                  # MIT 许可证
```

## 环境变量

| 变量 | 用途 | 必需 |
|------|------|------|
| `DOUBAO_APPID` | 火山引擎应用 ID | TTS + ASR |
| `DOUBAO_TOKEN` | 火山引擎访问令牌 | TTS + ASR |
| `DOUBAO_CLUSTER` | 火山引擎集群 | ASR |

## API 端点

- **TTS**: `https://openspeech.bytedance.com/api/v3/tts/unidirectional` (HTTP 流式)
- **ASR**: `wss://openspeech.bytedance.com/api/v2/asr` (WebSocket)

---

## 代码提交工作流

**每次提交代码前必须严格执行以下检查流程：**

### 1. 语法检查

```bash
# Python 语法检查
python3 -m py_compile skills/doubao-tts/scripts/tts.py
python3 -m py_compile skills/doubao-asr/scripts/asr.py

# Shell 语法检查
bash -n scripts/install-openclaw.sh
```

### 2. 代码与文档一致性检查

检查项：
- [ ] SKILL.md 中的参数与 Python 脚本的 argparse 参数一致
- [ ] SKILL.md 中的默认值与 Python 脚本的默认值一致
- [ ] SKILL.md 中的 API 端点与 Python 脚本的端点一致
- [ ] README.md 中的用法示例与实际脚本参数一致
- [ ] 错误码说明与脚本中的 ERROR_CODES 一致

### 3. 文档排版检查

检查项：
- [ ] 标题层级正确（# ## ### 递进）
- [ ] 代码块使用正确的语言标记（bash, python, json）
- [ ] 表格格式对齐
- [ ] 链接有效
- [ ] 无拼写错误

### 4. SKILL.md 意图识别检查

检查项：
- [ ] YAML frontmatter 格式正确（name, description, metadata）
- [ ] description 包含英文关键词（TTS, ASR, speech, audio, voice, transcribe）
- [ ] description 末尾包含中文意图关键词（豆包语音合成，语音转文字 等）
- [ ] metadata.openclaw.requires 正确列出依赖（bins, env）
- [ ] metadata.openclaw.primaryEnv 设置为 DOUBAO_TOKEN
- [ ] 脚本路径使用 `{baseDir}` 占位符

### 5. 更新 CHANGELOG.md

- 按照 Keep a Changelog 规范记录变更
- 使用语义化版本号（MAJOR.MINOR.PATCH）
- 分类：Added, Changed, Fixed, Removed

### 6. 提交和推送

```bash
# 提交（不带 Co-Authored-By）
git add .
git commit -m "feat/fix/docs: 简洁描述"

# 打标签（发布版本时）
git tag -a v1.0.0 -m "Release v1.0.0"

# 推送
git push origin main --tags
```

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-02-07 | 初始发布 |

---

## 注意事项

1. **SKILL.md 保持英文**，仅在 description 末尾添加中文意图关键词
2. **README.md 使用中文**，面向中文用户
3. **提交信息不带 Co-Authored-By**
4. **占位符检查**：发布前确保无 `your-username` 占位符
