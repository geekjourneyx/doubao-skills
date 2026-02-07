# Claude Skills 规范与最佳实践

> 本文档整理了 Claude 官方 Skills 开发规范、OpenClaw 平台规范、ClawHub 发布规范，用于指导豆包语音服务 Skills 的开发。

---

## 目录

1. [核心原则](#一核心原则)
2. [Skill 结构规范](#二skill-结构规范)
3. [渐进式披露模式](#三渐进式披露模式)
4. [可执行代码规范](#四可执行代码规范)
5. [OpenClaw 平台规范](#五openclaw-平台规范)
6. [ClawHub 发布规范](#六clawhub-发布规范)
7. [有效 Skill 检查清单](#七有效-skill-检查清单)
8. [豆包 Skills 设计参考](#八豆包-skills-设计参考)

---

## 一、核心原则

### 1.1 简洁至上

Context window 是公共资源，每个 token 都要物有所值。

**默认假设**: Claude 已经很聪明，只添加它不知道的信息。

挑战每一段落：
- "Claude 真的需要这个解释吗？"
- "可以假设 Claude 知道这个吗？"
- "这段内容值得消耗这些 token 吗？"

**简洁示例** (~50 tokens):
```markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

### 1.2 设置适当的自由度

根据任务脆弱性和可变性决定指令的具体程度：

| 自由度 | 适用场景 | 示例 |
|--------|----------|------|
| **高自由度** | 多种有效方法、依赖上下文判断 | 代码审查流程 |
| **中自由度** | 有首选模式、允许变化 | 生成报告（带模板） |
| **低自由度** | 易错、一致性关键、必须按序 | 数据库迁移、API 调用 |

**比喻**: 把 Claude 想象成探索路径的机器人
- 窄桥悬崖 → 提供具体护栏和精确指令（低自由度）
- 开阔平原 → 给出大致方向，信任 Claude 找路（高自由度）

### 1.3 在所有计划使用的模型上测试

| 模型 | 测试重点 |
|------|----------|
| **Haiku** | 是否提供足够指导？ |
| **Sonnet** | 是否清晰高效？ |
| **Opus** | 是否过度解释？ |

---

## 二、Skill 结构规范

### 2.1 YAML Frontmatter 要求

```yaml
---
name: max-64-chars-only-lowercase-numbers-hyphens
description: 非空，max-1024字符，说明做什么+何时使用
---
```

### 2.2 name 字段规则

| 规则 | 说明 |
|------|------|
| 最大长度 | 64 字符 |
| 允许字符 | 小写字母、数字、连字符 |
| 禁止内容 | XML 标签、保留词 (anthropic, claude) |
| 不能以连字符开头/结尾 | `my-skill` ✅, `-my-skill` ❌ |
| 不能有连续连字符 | `my-skill` ✅, `my--skill` ❌ |

### 2.3 description 字段规则

| 规则 | 说明 |
|------|------|
| 必须非空 | ✓ |
| 最大长度 | 1024 字符 |
| 禁止内容 | XML 标签、尖括号 `< >` |
| **必须用第三人称** | 会注入 system prompt |

**示例**:
- ✅ `"Processes Excel files and generates reports"`
- ❌ `"I can help you process Excel files"`
- ❌ `"You can use this to process Excel files"`

### 2.4 命名约定

推荐使用 **动名词形式 (gerund form)**:

| 推荐 | 可接受 | 避免 |
|------|--------|------|
| `processing-pdfs` | `pdf-processing` | `helper`, `utils` |
| `analyzing-spreadsheets` | `spreadsheet-analysis` | `documents`, `data` |
| `synthesizing-speech` | `speech-synthesis` | `tools`, `files` |

### 2.5 描述写作技巧

**具体且包含关键术语**:

```yaml
description: Synthesizes speech from text using Doubao TTS API.
Use when converting text to audio, generating voice content, or when the user mentions speech synthesis, TTS, or voice generation.
```

---

## 三、渐进式披露模式

SKILL.md 作为目录，按需加载其他内容。

### 3.1 目录结构示例

```
skill/
├── SKILL.md              # 主指令（触发时加载）
├── REFERENCE.md          # API 参考（按需）
├── EXAMPLES.md           # 使用示例（按需）
└── scripts/
    ├── tts.py            # TTS 执行脚本
    ├── asr.py            # ASR 执行脚本
    └── utils.py          # 工具函数
```

### 3.2 关键规则

1. **SKILL.md 主体保持在 500 行以内**
2. **引用只保持一层深度**，避免嵌套引用
3. **长文件（>100 行）顶部添加目录**

**反模式 - 嵌套过深**:
```markdown
# SKILL.md → advanced.md → details.md → actual info
```

**正确模式 - 一层引用**:
```markdown
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [ADVANCED.md](ADVANCED.md)
**API reference**: See [REFERENCE.md](REFERENCE.md)
**Examples**: See [EXAMPLES.md](EXAMPLES.md)
```

### 3.3 组织模式

**模式 1: 高级指南 + 引用**

```markdown
---
name: doubao-tts
description: Synthesizes speech from text using Doubao TTS API...
---

# Doubao TTS

## Quick start

[基本使用说明]

## Advanced features

**Voice types**: See [VOICES.md](VOICES.md)
**API reference**: See [REFERENCE.md](REFERENCE.md)
```

**模式 2: 按功能组织**

```markdown
# Doubao Speech Services

## Available services

**TTS (Text-to-Speech)**: See [TTS.md](TTS.md)
**ASR (Speech-to-Text)**: See [ASR.md](ASR.md)
```

---

## 四、可执行代码规范

### 4.1 解决问题而非推诿

**好的示例 - 显式处理错误**:
```python
def synthesize_speech(text: str, voice_type: str):
    """Synthesize speech, handling common errors gracefully."""
    try:
        # 检查配置
        if not os.getenv("DOUBAO_APPID"):
            print("Error: DOUBAO_APPID not set. Please configure environment.")
            return None

        # 执行合成
        result = await tts_client.synthesize(text, voice_type)
        return result

    except ConnectionError:
        print("Network error. Please check your connection.")
        return None
    except AuthenticationError:
        print("Invalid credentials. Please verify DOUBAO_TOKEN.")
        return None
```

**坏的示例 - 推给 Claude**:
```python
def synthesize_speech(text, voice_type):
    # Just fail and let Claude figure it out
    return tts_client.synthesize(text, voice_type)
```

### 4.2 配置参数要有文档

避免 "voodoo constants":

**好的示例**:
```python
# WebSocket connections typically complete within 30 seconds
# Longer timeout accounts for slow network conditions
WEBSOCKET_TIMEOUT = 30

# Audio segments are sent in 100ms chunks for real-time streaming
# This balances latency and network efficiency
AUDIO_SEGMENT_MS = 100
```

**坏的示例**:
```python
TIMEOUT = 47  # Why 47?
CHUNK = 3200  # Why 3200?
```

### 4.3 依赖管理

**不要假设包已安装**:

```markdown
## Prerequisites

Install required package:
```bash
pip install websockets>=14.0
```

Then use it:
```python
import websockets
# ...
```
```

### 4.4 脚本区分：执行 vs 参考

明确指令：
- **执行脚本**: "Run `scripts/tts.py` to synthesize speech"
- **作为参考阅读**: "See `scripts/tts.py` for the synthesis algorithm"

---

## 五、OpenClaw 平台规范

### 5.1 加载位置和优先级

Skills 从三个位置加载：

| 位置 | 说明 | 优先级 |
|------|------|--------|
| `<workspace>/skills` | 工作区 Skills | 最高 |
| `~/.openclaw/skills` | 管理/本地 Skills | 中 |
| 捆绑 Skills | 随安装包提供 | 最低 |

### 5.2 Gating 机制（加载时过滤）

```yaml
---
name: doubao-tts
description: Synthesizes speech from text using Doubao TTS API.
metadata:
  {
    "openclaw":
      {
        "requires": {
          "bins": ["python3"],
          "env": ["DOUBAO_APPID", "DOUBAO_TOKEN"]
        },
        "primaryEnv": "DOUBAO_TOKEN",
      },
  }
---
```

**Gating 字段说明**:

| 字段 | 说明 |
|------|------|
| `always: true` | 跳过其他检查，始终加载 |
| `emoji` | macOS Skills UI 使用的 emoji |
| `os` | 限制平台 (`darwin`, `linux`, `win32`) |
| `requires.bins` | 必须存在于 PATH 的二进制文件列表 |
| `requires.anyBins` | 至少一个必须存在 |
| `requires.env` | 必须存在的环境变量 |
| `requires.config` | openclaw.json 中必须为 truthy 的路径 |
| `primaryEnv` | 关联 `skills.entries.<name>.apiKey` 的环境变量 |

### 5.3 配置覆盖

在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "skills": {
    "entries": {
      "doubao-tts": {
        "enabled": true,
        "env": {
          "DOUBAO_APPID": "your-appid",
          "DOUBAO_TOKEN": "your-token"
        }
      }
    }
  }
}
```

### 5.4 环境注入

每次 agent 运行时：
1. 读取 skill metadata
2. 应用 `skills.entries.<key>.env` 到 `process.env`
3. 构建 system prompt
4. 运行结束后恢复原始环境

**作用域**: 仅限当前 agent 运行，不是全局 shell 环境。

### 5.5 Token 影响

Skills 注入 system prompt 的成本：
- 基础开销（≥1 skill）: 195 字符
- 每个 skill: 97 字符 + name + description + location 长度

**公式**:
```
total = 195 + Σ (97 + len(name) + len(description) + len(location))
```

---

## 六、ClawHub 发布规范

### 6.1 ClawHub 简介

ClawHub 是 OpenClaw 的公共 Skills 注册表：
- 公开浏览所有 Skills
- 向量搜索（不仅是关键词）
- 版本管理（semver、changelog、tags）
- 社区反馈（stars、comments）
- 审核机制

### 6.2 CLI 命令

```bash
# 安装 CLI
npm i -g clawhub

# 搜索
clawhub search "speech synthesis"

# 安装
clawhub install <skill-slug>

# 更新
clawhub update --all

# 发布
clawhub publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0

# 同步（扫描 + 发布更新）
clawhub sync --all
```

### 6.3 发布要求

| 要求 | 说明 |
|------|------|
| GitHub 账号 | 至少 1 周 |
| SKILL.md | 必须包含 name 和 description |
| 版本 | Semver 格式 |
| 唯一 slug | 全局唯一的标识符 |

### 6.4 版本管理

- 每次发布创建新的 semver 版本
- Tags（如 `latest`）指向特定版本
- Changelogs 附加到每个版本
- 支持回滚到历史版本

---

## 七、有效 Skill 检查清单

### 7.1 核心质量

- [ ] 描述具体且包含关键术语
- [ ] 描述包含做什么 + 何时使用
- [ ] 始终用第三人称描述
- [ ] SKILL.md 主体 < 500 行
- [ ] 无时效性信息（或在 "old patterns" 部分）
- [ ] 术语一致
- [ ] 引用仅一层深
- [ ] 使用渐进式披露

### 7.2 代码和脚本

- [ ] 脚本解决问题而非推给 Claude
- [ ] 显式错误处理
- [ ] 无魔法数字（所有值都有说明）
- [ ] 列出所需包
- [ ] 无 Windows 风格路径
- [ ] 关键操作有验证步骤

### 7.3 测试

- [ ] 至少 3 个评估场景
- [ ] 在 Haiku/Sonnet/Opus 上测试
- [ ] 真实使用场景测试

### 7.4 OpenClaw 兼容

- [ ] 正确的 YAML frontmatter
- [ ] metadata.openclaw 配置（如需要）
- [ ] 环境变量使用 requires.env 声明
- [ ] 二进制依赖使用 requires.bins 声明

---

## 八、豆包 Skills 设计参考

基于上述规范，豆包语音服务 Skills 的设计建议：

### 8.1 建议的 Skill 结构

```
doubao-tts/
├── SKILL.md              # 主文件 (< 500 行)
├── VOICES.md             # 音色列表参考
├── EXAMPLES.md           # 使用示例
└── scripts/
    ├── tts.py            # TTS 执行脚本
    └── utils.py          # 工具函数

doubao-asr/
├── SKILL.md              # 主文件 (< 500 行)
├── WORKFLOW.md           # Workflow 配置参考
├── EXAMPLES.md           # 使用示例
└── scripts/
    ├── asr.py            # ASR 执行脚本
    └── utils.py          # 工具函数
```

### 8.2 YAML Frontmatter 示例

**TTS Skill**:
```yaml
---
name: doubao-tts
description: Synthesizes speech from text using Doubao (ByteDance) TTS API.
Supports multiple voice types, emotions, and audio formats.
Use when converting text to audio or generating voice content.
metadata:
  {
    "openclaw":
      {
        "requires": {
          "bins": ["python3"],
          "env": ["DOUBAO_APPID", "DOUBAO_TOKEN"]
        },
        "primaryEnv": "DOUBAO_TOKEN",
      },
  }
---
```

**ASR Skill**:
```yaml
---
name: doubao-asr
description: Transcribes audio to text using Doubao (ByteDance) ASR API.
Supports streaming recognition, multiple audio formats, and Chinese/English.
Use when converting speech to text or transcribing audio files.
metadata:
  {
    "openclaw":
      {
        "requires": {
          "bins": ["python3"],
          "env": ["DOUBAO_APPID", "DOUBAO_TOKEN", "DOUBAO_CLUSTER"]
        },
        "primaryEnv": "DOUBAO_TOKEN",
      },
  }
---
```

### 8.3 自由度设计

| 功能 | 自由度 | 原因 |
|------|--------|------|
| TTS 基本调用 | 低 | 必须按照 API 规范，参数有严格要求 |
| 音色选择 | 中 | 用户可能有偏好，但有默认值 |
| ASR 音频分段 | 低 | 必须按照协议规范 |
| 输出格式选择 | 中 | 有默认值，允许用户选择 |

### 8.4 错误处理设计

```python
# 错误码映射
TTS_ERRORS = {
    3000: "Success",
    3001: "Invalid request - check parameters",
    3003: "Concurrent limit exceeded - retry later",
    3010: "Text too long - split into smaller chunks",
    3050: "Voice type not found - check voice_type parameter",
}

ASR_ERRORS = {
    1000: "Success",
    1001: "Invalid parameters - check request format",
    1002: "Authentication failed - verify token",
    1013: "Silent audio - no speech detected",
}
```

---

## 附录

### A. 参考文档

| 文档 | 位置 | 说明 |
|------|------|------|
| SKILL-RULE.md | `/root/skill-rules/SKILL-RULE.md` | Claude 官方最佳实践 |
| openclaw.md | `/root/skill-rules/openclaw.md` | OpenClaw 平台规范 |
| clawhub.md | `/root/skill-rules/clawhub.md` | ClawHub 发布规范 |
| architecture.md | `/root/doubao-skills/docs/architecture.md` | 豆包语音服务架构 |

### B. 开发流程

1. **先不用 Skill 完成任务** → 注意反复提供的信息
2. **用 Claude A 创建 Skill** → 让它帮忙生成结构
3. **用 Claude B 测试** → 新实例测试真实任务
4. **观察并迭代** → 基于实际行为而非假设改进

---

*文档版本: 1.0*
*最后更新: 2026-02-07*
