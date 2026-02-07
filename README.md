# 豆包语音服务 Skills

> 字节跳动火山引擎语音服务的 Claude Code 插件（TTS 语音合成 + ASR 语音识别）

---

## 功能特性

| Skill | 功能 | 亮点 |
|-------|------|------|
| **doubao-tts** | 文字转语音 | 100+ 音色、情感控制、语速调节 |
| **doubao-asr** | 语音转文字 | 流式识别、ITN、标点、多语言 |

---

## 安装方式

### 方式一：一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/geekjourneyx/doubao-skills/main/scripts/install-openclaw.sh | bash
```

### 方式二：npx skills

```bash
# 从 GitHub 安装
npx skills add geekjourneyx/doubao-skills

# 查看可用 skills
npx skills add geekjourneyx/doubao-skills --list

# 安装指定 skill
npx skills add geekjourneyx/doubao-skills --skill doubao-tts

# 安装到指定 agent
npx skills add geekjourneyx/doubao-skills -a claude-code -a cursor
```

### 方式二：Claude Code 插件

```bash
# 添加市场
/plugin marketplace add geekjourneyx/doubao-skills

# 安装插件
/plugin install doubao-speech@geekjourneyx/doubao-skills
```

或浏览：`/plugin > Discover > 搜索 "doubao"`

### 方式三：直接从 GitHub 安装

```bash
/plugin install https://github.com/geekjourneyx/doubao-skills.git
```

### 方式四：手动安装

```bash
git clone https://github.com/geekjourneyx/doubao-skills.git
cp -r doubao-skills/skills/* ~/.claude/skills/
```

---

## 配置说明

### 第一步：获取 API 凭证

1. 访问 [火山引擎控制台](https://console.volcengine.com/speech/service/8)
2. 创建应用
3. 获取 **App ID**、**Access Token** 和 **Cluster**

### 第二步：设置环境变量

```bash
export DOUBAO_APPID="your-appid"
export DOUBAO_TOKEN="your-access-token"
export DOUBAO_CLUSTER="your-cluster"  # ASR 必需
```

### 第三步：安装 Python 依赖

```bash
pip install requests websockets
```

---

## 使用方法

### TTS 语音合成

**基本用法：**

```bash
python skills/doubao-tts/scripts/tts.py --text "你好，世界！"
```

**完整参数：**

```bash
python skills/doubao-tts/scripts/tts.py \
  --text "欢迎使用豆包语音合成服务。" \
  --voice_type zh_female_cancan_mars_bigtts \
  --encoding mp3 \
  --speed_ratio 1.0 \
  --output welcome.mp3
```

**参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--text` | (必填) | 要合成的文本 |
| `--voice_type` | `zh_female_cancan_mars_bigtts` | 音色 ID |
| `--encoding` | `mp3` | 格式：mp3/wav/pcm/ogg_opus |
| `--speed_ratio` | `1.0` | 语速：0.1 - 2.0 |
| `--emotion` | - | 情感（支持的音色） |
| `--output` | `output.<格式>` | 输出文件 |

### ASR 语音识别

**基本用法：**

```bash
python skills/doubao-asr/scripts/asr.py --audio_path recording.wav
```

**完整参数：**

```bash
python skills/doubao-asr/scripts/asr.py \
  --audio_path speech.wav \
  --format wav \
  --language zh-CN \
  --workflow full \
  --show_utterances
```

**参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--audio_path` | (必填) | 音频文件路径 |
| `--format` | `wav` | 格式：wav/mp3/raw/ogg |
| `--language` | `zh-CN` | 语言代码 |
| `--workflow` | `full` | 处理流程 |
| `--show_utterances` | `false` | 显示时间戳 |

---

## 常用音色

| 音色 ID | 类型 | 说明 |
|---------|------|------|
| `zh_female_cancan_mars_bigtts` | 女声 | 灿灿（默认） |
| `zh_male_rap_mars_bigtts` | 男声 | 说唱风格 |
| `zh_female_shuangkuaisisi_moon_bigtts` | 女声 | 支持多情感 |

完整列表见 [VOICES.md](skills/doubao-tts/VOICES.md)。

---

## 处理流程选项（ASR）

| 选项 | 功能 |
|------|------|
| `default` | 基础识别 |
| `itn` | + 数字规范化 |
| `punctuate` | + 标点符号 |
| `smooth` | + 口语顺滑 |
| `full` | 全部功能 |

详细说明见 [WORKFLOW.md](skills/doubao-asr/WORKFLOW.md)。

---

## 项目结构

```
doubao-skills/
├── .claude-plugin/
│   ├── plugin.json              # 插件清单
│   └── marketplace.json         # 市场配置
├── scripts/
│   └── install-openclaw.sh      # 一键安装脚本
├── skills/
│   ├── doubao-tts/
│   │   ├── SKILL.md             # TTS 技能定义
│   │   ├── VOICES.md            # 音色参考
│   │   └── scripts/tts.py       # TTS 脚本
│   └── doubao-asr/
│       ├── SKILL.md             # ASR 技能定义
│       ├── WORKFLOW.md          # 流程参考
│       └── scripts/asr.py       # ASR 脚本
├── docs/
│   ├── architecture.md          # 架构文档
│   └── skills-specification.md  # 规范文档
├── README.md
└── LICENSE
```

---

## 错误码说明

### TTS 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 3000 | 成功 | - |
| 3001 | 请求无效 | 检查参数 |
| 3003 | 并发超限 | 稍后重试 |
| 3010 | 文本过长 | 拆分文本 |
| 3050 | 音色不存在 | 检查 voice_type |

### ASR 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 1000 | 成功 | - |
| 1002 | 认证失败 | 检查 token |
| 1013 | 静音音频 | 检查音频内容 |
| 1020 | 超时 | 重试 |

---

## 发布到 GitHub

```bash
git init
git add .
git commit -m "v1.0.0"
git remote add origin https://github.com/geekjourneyx/doubao-skills.git
git push -u origin main
```

发布后，用户即可安装：

```bash
npx skills add geekjourneyx/doubao-skills
```

---

## API 参考

### TTS 接口

- **地址**：`https://openspeech.bytedance.com/api/v3/tts/unidirectional`
- **方式**：HTTP POST（流式响应）
- **认证**：`Authorization: Bearer; {token}`

### ASR 接口

- **地址**：`wss://openspeech.bytedance.com/api/v2/asr`
- **协议**：WebSocket（二进制帧）
- **认证**：`Authorization: Bearer; {token}`

---

## 相关文档

- [架构文档](docs/architecture.md)
- [Skills 规范](docs/skills-specification.md)
- [火山引擎 TTS 文档](https://www.volcengine.com/docs/6561/1257584)
- [火山引擎 ASR 文档](https://www.volcengine.com/docs/6561/80816)

---

## 环境要求

- Python 3.9+
- `requests`（TTS）
- `websockets`（ASR）

---

## 许可证

MIT License - 见 [LICENSE](LICENSE)

---

## 贡献

1. Fork 本仓库
2. 创建特性分支
3. 提交 Pull Request

---

## 支持

- [GitHub Issues](https://github.com/geekjourneyx/doubao-skills/issues)
- [火山引擎文档](https://www.volcengine.com/docs/6561/1257584)
