# 豆包语音服务 SDK 核心架构文档

> 本文档详细记录了火山引擎豆包语音服务（TTS 语音合成 + ASR 语音识别）的核心架构、协议规范、交互流程和代码实现细节。

---

## 目录

1. [项目概述](#一项目概述)
2. [整体架构图](#二整体架构图)
3. [WebSocket 二进制协议](#三websocket-二进制协议)
4. [TTS 语音合成](#四tts-语音合成)
5. [ASR 语音识别](#五asr-语音识别)
6. [核心参数传递机制](#六核心参数传递机制)
7. [错误处理机制](#七错误处理机制)
8. [环境变量与配置](#八环境变量与配置)
9. [关键代码路径](#九关键代码路径)
10. [Skills 封装建议](#十skills-封装建议)

---

## 一、项目概述

### 1.1 基本信息

| 项目 | 说明 |
|------|------|
| 项目名称 | volc-speech-python-sdk |
| 开发语言 | Python 3.9+ |
| 核心依赖 | websockets >= 14.0 |
| 协议类型 | WebSocket 二进制协议 |

### 1.2 功能模块

- **TTS (Text-to-Speech)**: 文本转语音，支持多种音色、情感、语速调节
- **ASR (Automatic Speech Recognition)**: 一句话识别，支持流式音频输入

### 1.3 项目结构

```
/root/doubao-skills/
├── protocols/                      # 核心协议实现
│   ├── __init__.py                 # 协议模块导出接口
│   └── protocols.py                # WebSocket 二进制协议实现 (544行)
├── asr/                            # 语音识别模块
│   └── streaming_asr_demo.py       # 流式语音识别演示 (358行)
├── examples/                       # 使用示例
│   └── volcengine/
│       └── binary.py               # TTS 二进制协议示例 (116行)
├── docs/                           # 文档目录
│   └── architecture.md             # 本架构文档
├── pyproject.toml                  # 项目元数据和依赖声明
├── setup.py                        # setuptools 安装配置
├── asr.md                          # 语音识别服务文档
└── voice.md                        # 语音合成服务文档
```

---

## 二、整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           豆包语音服务 SDK 架构                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        应用层 (Application Layer)                    │   │
│  │  ┌──────────────────────┐      ┌──────────────────────┐            │   │
│  │  │   TTS Demo           │      │   ASR Demo           │            │   │
│  │  │ (binary.py)          │      │ (streaming_asr_demo) │            │   │
│  │  │                      │      │                      │            │   │
│  │  │ • 命令行参数解析      │      │ • 音频文件读取        │            │   │
│  │  │ • 请求构建           │      │ • 请求构建           │            │   │
│  │  │ • 音频文件保存       │      │ • 分段发送           │            │   │
│  │  └──────────┬───────────┘      └──────────┬───────────┘            │   │
│  └─────────────┼─────────────────────────────┼───────────────────────-┘   │
│                │                             │                             │
│  ┌─────────────▼─────────────────────────────▼───────────────────────-┐   │
│  │                     协议层 (Protocol Layer)                         │   │
│  │                      protocols/protocols.py                         │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Message 类 (核心)                         │   │   │
│  │  │  • marshal()    → 序列化为二进制                            │   │   │
│  │  │  • unmarshal()  → 从二进制反序列化                          │   │   │
│  │  │  • from_bytes() → 工厂方法                                  │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    枚举类定义                                 │   │   │
│  │  │  • MsgType         (消息类型)                               │   │   │
│  │  │  • MsgTypeFlagBits (消息标志)                               │   │   │
│  │  │  • EventType       (事件类型 150+种)                        │   │   │
│  │  │  • SerializationBits / CompressionBits                      │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    异步通信函数                               │   │   │
│  │  │  • full_client_request()  • receive_message()               │   │   │
│  │  │  • audio_only_client()    • wait_for_event()                │   │   │
│  │  │  • start/finish_connection/session()                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
│  ┌─────────────────────────────────▼───────────────────────────────────┐   │
│  │                     传输层 (Transport Layer)                         │   │
│  │                       websockets 库                                  │   │
│  │  • WebSocket 双向通信                                                │   │
│  │  • 支持 wss:// 加密连接                                              │   │
│  │  • Header 认证 (Bearer Token / HMAC256)                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                       │
└────────────────────────────────────┼───────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          火山引擎云端服务                                     │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐          │
│  │   TTS 服务                   │  │   ASR 服务                   │          │
│  │   /api/v1/tts/ws_binary     │  │   /api/v2/asr               │          │
│  │   wss://openspeech.         │  │   wss://openspeech.         │          │
│  │   bytedance.com             │  │   bytedance.com             │          │
│  └─────────────────────────────┘  └─────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 三、WebSocket 二进制协议

### 3.1 报文格式

```
┌────────────────────────────────────────────────────────────────────────┐
│                     WebSocket 二进制协议报文格式                         │
├────────────────────────────────────────────────────────────────────────┤
│ Byte 0          │ Byte 1          │ Byte 2          │ Byte 3          │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Version │ HSize │ MsgType │ Flags │ Serial  │ Comp  │    Reserved     │
│ (4bit)  │(4bit) │ (4bit)  │(4bit) │ (4bit)  │(4bit) │    (8 bits)     │
├─────────────────┴─────────────────┴─────────────────┴─────────────────┤
│                    [Optional Header Extensions]                        │
├───────────────────────────────────────────────────────────────────────┤
│                    Payload Size (4 bytes, Big Endian)                  │
├───────────────────────────────────────────────────────────────────────┤
│                    Payload (variable length)                           │
│                    (JSON/Raw bytes, 可 Gzip 压缩)                       │
└───────────────────────────────────────────────────────────────────────┘
```

### 3.2 字段说明

| 字段 | 位数 | 说明 | 可选值 |
|------|------|------|--------|
| Protocol Version | 4 | 协议版本 | `0b0001` = Version 1 |
| Header Size | 4 | 头部大小 (实际 = value × 4 bytes) | `0b0001` = 4 bytes |
| Message Type | 4 | 消息类型 | 见下表 |
| Flags | 4 | 消息标志 | 见下表 |
| Serialization | 4 | 序列化方式 | `0b0000`=Raw, `0b0001`=JSON |
| Compression | 4 | 压缩方式 | `0b0000`=None, `0b0001`=Gzip |
| Reserved | 8 | 保留字段 | `0x00` |

### 3.3 消息类型 (MsgType)

| 值 | 名称 | 说明 |
|----|------|------|
| `0b0001` | FullClientRequest | 客户端发送完整请求 (含 JSON 参数) |
| `0b0010` | AudioOnlyClient | 客户端发送音频数据 |
| `0b1001` | FullServerResponse | 服务端完整响应 |
| `0b1011` | AudioOnlyServer | 服务端音频响应/ACK |
| `0b1100` | FrontEndResultServer | 服务端前端处理结果 |
| `0b1111` | Error | 错误消息 |

### 3.4 消息标志 (Flags)

| 值 | 名称 | 说明 |
|----|------|------|
| `0b0000` | NoSeq | 无序列号 |
| `0b0001` | PositiveSeq | 正序列号 (sequence > 0) |
| `0b0010` | LastNoSeq | 最后一包，无序列号 |
| `0b0011` | NegativeSeq | 负序列号 (sequence < 0)，表示最后一包 |
| `0b0100` | WithEvent | 包含事件号 |

### 3.5 核心代码实现

```python
# protocols/protocols.py - Message 类核心方法

@dataclass
class Message:
    version: VersionBits = VersionBits.Version1
    header_size: HeaderSizeBits = HeaderSizeBits.HeaderSize4
    type: MsgType = MsgType.Invalid
    flag: MsgTypeFlagBits = MsgTypeFlagBits.NoSeq
    serialization: SerializationBits = SerializationBits.JSON
    compression: CompressionBits = CompressionBits.None_
    payload: bytes = b""

    def marshal(self) -> bytes:
        """序列化消息为二进制"""
        buffer = io.BytesIO()
        header = [
            (self.version << 4) | self.header_size,
            (self.type << 4) | self.flag,
            (self.serialization << 4) | self.compression,
        ]
        # ... 写入 header 和 payload
        return buffer.getvalue()

    def unmarshal(self, data: bytes) -> None:
        """从二进制反序列化消息"""
        # 解析 header 字段
        # 解析 payload
```

---

## 四、TTS 语音合成

### 4.1 服务端点

| 版本 | 端点 | 说明 |
|------|------|------|
| V1 WebSocket | `wss://openspeech.bytedance.com/api/v1/tts/ws_binary` | 单向流式 |
| V1 HTTP | `https://openspeech.bytedance.com/api/v1/tts` | 非流式 |
| V3 WebSocket | `wss://openspeech.bytedance.com/api/v3/tts/bidirection` | 双向流式 |

### 4.2 交互流程

```
┌─────────────┐                                    ┌─────────────────┐
│   Client    │                                    │   TTS Server    │
└──────┬──────┘                                    └────────┬────────┘
       │                                                    │
       │  1. WebSocket 连接 + Bearer Token 认证             │
       │ ──────────────────────────────────────────────────>│
       │                                                    │
       │  2. FullClientRequest (JSON payload)               │
       │     {app, user, audio, request}                    │
       │ ──────────────────────────────────────────────────>│
       │                                                    │
       │  3. FrontEndResultServer (可选，前端处理结果)        │
       │ <──────────────────────────────────────────────────│
       │                                                    │
       │  4. AudioOnlyServer (sequence > 0, 音频片段)        │
       │ <──────────────────────────────────────────────────│
       │                                                    │
       │  5. AudioOnlyServer (sequence > 0, 更多音频片段)    │
       │ <──────────────────────────────────────────────────│
       │                                                    │
       │  6. AudioOnlyServer (sequence < 0, 最后一包)        │
       │ <──────────────────────────────────────────────────│
       │                                                    │
       │  7. 关闭连接                                        │
       │ ──────────────────────────────────────────────────>│
       ▼                                                    ▼
```

### 4.3 请求参数

```python
{
    "app": {
        "appid": str,      # 必填: 应用ID
        "token": str,      # 必填: Access Token
        "cluster": str     # 必填: "volcano_tts" 或 "volcano_icl"
    },
    "user": {
        "uid": str         # 必填: 用户标识 (可传任意非空字符串)
    },
    "audio": {
        "voice_type": str,     # 必填: 音色ID
        "encoding": str,       # 可选: wav/pcm/mp3/ogg_opus, 默认pcm
        "speed_ratio": float,  # 可选: 语速 [0.1, 2], 默认1
        "rate": int,           # 可选: 采样率, 默认24000
        "emotion": str,        # 可选: 情感 (angry, happy等)
        "enable_emotion": bool,# 可选: 是否启用情感
        "loudness_ratio": float# 可选: 音量 [0.5, 2], 默认1
    },
    "request": {
        "reqid": str,          # 必填: 唯一请求ID (建议UUID)
        "text": str,           # 必填: 合成文本 (≤1024字节, 建议<300字符)
        "operation": str,      # 必填: "submit"(流式) / "query"(非流式)
        "with_timestamp": "1", # 可选: 启用时间戳
        "text_type": str,      # 可选: "ssml" 使用SSML标记
        "extra_param": str     # 可选: JSON字符串，额外参数
    }
}
```

### 4.4 音色类型

| Cluster | 说明 | 音色前缀示例 |
|---------|------|-------------|
| `volcano_tts` | 标准音色 | `zh_female_cancan_mars_bigtts` |
| `volcano_icl` | ICL复刻音色 | `S_` 开头 |

### 4.5 代码示例

```python
# examples/volcengine/binary.py 核心流程

async def main():
    # 1. 建立连接
    headers = {"Authorization": f"Bearer;{access_token}"}
    websocket = await websockets.connect(endpoint, additional_headers=headers)

    # 2. 构建请求
    request = {
        "app": {"appid": appid, "token": access_token, "cluster": cluster},
        "user": {"uid": str(uuid.uuid4())},
        "audio": {"voice_type": voice_type, "encoding": encoding},
        "request": {"reqid": str(uuid.uuid4()), "text": text, "operation": "submit"}
    }

    # 3. 发送请求
    await full_client_request(websocket, json.dumps(request).encode())

    # 4. 接收音频
    audio_data = bytearray()
    while True:
        msg = await receive_message(websocket)
        if msg.type == MsgType.AudioOnlyServer:
            audio_data.extend(msg.payload)
            if msg.sequence < 0:  # 最后一包
                break

    # 5. 保存文件
    with open(f"{voice_type}.{encoding}", "wb") as f:
        f.write(audio_data)
```

---

## 五、ASR 语音识别

### 5.1 服务端点

| 端点 | 说明 |
|------|------|
| `wss://openspeech.bytedance.com/api/v2/asr` | 一句话识别 WebSocket |

### 5.2 交互流程

```
┌─────────────┐                                    ┌─────────────────┐
│   Client    │                                    │   ASR Server    │
└──────┬──────┘                                    └────────┬────────┘
       │                                                    │
       │  1. WebSocket 连接 + Bearer Token 认证             │
       │ ──────────────────────────────────────────────────>│
       │                                                    │
       │  2. FullClientRequest (JSON: app, user, audio,     │
       │     request 包含 workflow 配置)                     │
       │ ──────────────────────────────────────────────────>│
       │                                                    │
       │  3. FullServerResponse (ACK, code=1000)            │
       │ <──────────────────────────────────────────────────│
       │                                                    │
       │  4. AudioOnlyRequest (音频分段1, flags=0b0000)      │
       │ ──────────────────────────────────────────────────>│
       │                                                    │
       │  5. FullServerResponse (中间识别结果)               │
       │ <──────────────────────────────────────────────────│
       │                                                    │
       │  6. AudioOnlyRequest (音频分段N, flags=0b0010=最后) │
       │ ──────────────────────────────────────────────────>│
       │                                                    │
       │  7. FullServerResponse (最终识别结果, sequence<0)   │
       │     {code, message, result: [{text, utterances}]}  │
       │ <──────────────────────────────────────────────────│
       ▼                                                    ▼
```

### 5.3 请求参数

```python
{
    "app": {
        "appid": str,      # 必填: 应用ID
        "token": str,      # 必填: Access Token
        "cluster": str     # 必填: 集群标识
    },
    "user": {
        "uid": str         # 必填: 用户标识
    },
    "audio": {
        "format": str,     # 必填: raw/wav/mp3/ogg
        "rate": int,       # 可选: 采样率, 默认16000
        "bits": int,       # 可选: 位深, 默认16
        "channel": int,    # 可选: 声道数, 默认1
        "codec": str,      # 可选: raw/opus, 默认raw
        "language": str    # 可选: "zh-CN"
    },
    "request": {
        "reqid": str,           # 必填: 唯一请求ID
        "sequence": int,        # 必填: 包序号 (1,2,3...,-N)
        "workflow": str,        # 可选: 处理流程
        "nbest": int,           # 可选: 候选数, 默认1
        "show_utterances": bool,# 可选: 显示分句信息
        "result_type": str,     # 可选: full/single
        "boosting_table_name": str,  # 可选: 热词表名称
        "correct_table_name": str    # 可选: 替换词表名称
    }
}
```

### 5.4 Workflow 配置

| Workflow | 说明 |
|----------|------|
| `audio_in,resample,partition,vad,fe,decode` | 默认：仅识别 |
| `...,itn` | 启用 ITN (反向文本规范化) |
| `...,nlu_punctuate` | 启用标点符号 |
| `...,nlu_ddc` | 启用顺滑 |
| `audio_in,resample,partition,vad,fe,decode,itn,nlu_ddc,nlu_punctuate` | 全部启用 |

### 5.5 响应格式

```json
{
  "reqid": "uuid",
  "code": 1000,
  "message": "Success",
  "sequence": -1,
  "result": [
    {
      "text": "识别结果文本",
      "confidence": 0.95,
      "utterances": [
        {
          "text": "分句文本",
          "start_time": 0,
          "end_time": 1705,
          "definite": true,
          "words": [
            {"text": "字", "start_time": 740, "end_time": 860}
          ]
        }
      ]
    }
  ],
  "addition": {
    "duration": "3696",
    "logid": "xxx"
  }
}
```

### 5.6 代码示例

```python
# asr/streaming_asr_demo.py 核心流程

class AsrWsClient:
    async def segment_data_processor(self, wav_data: bytes, segment_size: int):
        reqid = str(uuid.uuid4())

        # 1. 构建请求
        request_params = self.construct_request(reqid)
        payload_bytes = gzip.compress(json.dumps(request_params).encode())

        # 2. 发送 full client request
        full_client_request = bytearray(generate_full_default_header())
        full_client_request.extend(len(payload_bytes).to_bytes(4, 'big'))
        full_client_request.extend(payload_bytes)

        # 3. 建立连接
        header = {'Authorization': f'Bearer; {self.token}'}
        async with websockets.connect(self.ws_url, extra_headers=header) as ws:
            await ws.send(full_client_request)
            res = await ws.recv()

            # 4. 分段发送音频
            for seq, (chunk, last) in enumerate(self.slice_data(wav_data, segment_size), 1):
                payload_bytes = gzip.compress(chunk)
                audio_request = bytearray(
                    generate_last_audio_default_header() if last
                    else generate_audio_default_header()
                )
                audio_request.extend(len(payload_bytes).to_bytes(4, 'big'))
                audio_request.extend(payload_bytes)

                await ws.send(audio_request)
                result = parse_response(await ws.recv())

        return result
```

---

## 六、核心参数传递机制

### 6.1 认证方式

```python
# Bearer Token 认证 (推荐)
headers = {
    "Authorization": "Bearer; {token}"  # 注意: Bearer 和 token 用分号分隔
}

# HMAC256 签名认证 (可选)
headers = {
    "Custom": "auth_custom",
    "Authorization": 'HMAC256; access_token="{token}"; mac="{mac}"; h="Custom"'
}
```

### 6.2 音频分段策略

```python
# ASR 音频分段
def slice_data(data: bytes, chunk_size: int):
    """将音频数据切分为固定大小的段"""
    offset = 0
    while offset + chunk_size < len(data):
        yield data[offset:offset + chunk_size], False  # 非最后一包
        offset += chunk_size
    yield data[offset:], True  # 最后一包

# 分段大小计算
# WAV: size_per_sec = nchannels * sampwidth * framerate
#      segment_size = size_per_sec * seg_duration / 1000
# MP3: 固定 10000 bytes
```

### 6.3 集群自动选择 (TTS)

```python
def get_cluster(voice: str) -> str:
    """根据音色自动选择集群"""
    if voice.startswith("S_"):
        return "volcano_icl"  # ICL 复刻音色
    return "volcano_tts"      # 标准音色
```

---

## 七、错误处理机制

### 7.1 TTS 错误码 (3xxx)

| 错误码 | 说明 | 建议处理 |
|--------|------|----------|
| 3000 | 成功 | 正常处理 |
| 3001 | 无效请求 | 检查参数 |
| 3003 | 并发超限 | 重试或降低并发 |
| 3005 | 服务器繁忙 | 重试 |
| 3006 | 服务中断 | 检查 reqid 唯一性 |
| 3010 | 文本长度超限 | 缩短文本 |
| 3011 | 无效文本 | 检查文本内容 |
| 3030 | 处理超时 | 重试 |
| 3050 | 音色不存在 | 检查 voice_type |

### 7.2 ASR 错误码 (1xxx)

| 错误码 | 说明 | 建议处理 |
|--------|------|----------|
| 1000 | 成功 | 正常处理 |
| 1001 | 参数无效 | 检查参数 |
| 1002 | 无访问权限 | 检查 token |
| 1003 | 访问超频 | 降低 QPS |
| 1004 | 访问超额 | 检查配额 |
| 1005 | 服务器繁忙 | 重试 |
| 1010 | 音频过长 | 缩短音频 |
| 1012 | 音频格式无效 | 检查格式 |
| 1013 | 音频静音 | 检查音频内容 |
| 1020 | 等待超时 | 重试 |
| 1022 | 识别错误 | 重试 |

### 7.3 代码中的错误检查

```python
# ASR 错误检查
result = parse_response(res)
if 'payload_msg' in result and result['payload_msg']['code'] != 1000:
    return result  # 提前返回错误

# TTS 错误检查
msg = await receive_message(websocket)
if msg.type == MsgType.Error:
    raise RuntimeError(f"TTS failed: {msg}")
```

---

## 八、环境变量与配置

### 8.1 必需配置

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `appid` | 应用 ID | 火山引擎控制台 |
| `token` | Access Token | 火山引擎控制台 |
| `cluster` | 集群标识 | 控制台创建应用后显示 |

### 8.2 ASR 配置示例

```python
# asr/streaming_asr_demo.py
appid = "xxx"           # 项目 APP ID
token = "xxx"           # 项目 Access Token
cluster = "xxx"         # 集群标识
audio_path = ""         # 本地音频路径
audio_format = "wav"    # 音频格式: wav/mp3
```

### 8.3 TTS 命令行参数

```bash
python3 examples/volcengine/binary.py \
    --appid <appid> \
    --access_token <access_token> \
    --voice_type <voice_type> \
    --text "合成文本" \
    --encoding wav \
    --cluster volcano_tts
```

### 8.4 服务端点

```python
# TTS
TTS_ENDPOINT_V1 = "wss://openspeech.bytedance.com/api/v1/tts/ws_binary"
TTS_ENDPOINT_V3 = "wss://openspeech.bytedance.com/api/v3/tts/bidirection"
TTS_HTTP = "https://openspeech.bytedance.com/api/v1/tts"

# ASR
ASR_ENDPOINT = "wss://openspeech.bytedance.com/api/v2/asr"
```

---

## 九、关键代码路径

| 功能 | 文件 | 核心函数/类 | 行号 |
|------|------|-------------|------|
| 二进制协议序列化 | `protocols/protocols.py` | `Message.marshal()` | 210-232 |
| 二进制协议反序列化 | `protocols/protocols.py` | `Message.unmarshal()` | 234-265 |
| 消息类型枚举 | `protocols/protocols.py` | `MsgType` | 13-28 |
| 事件类型枚举 | `protocols/protocols.py` | `EventType` | 76-150 |
| 异步消息接收 | `protocols/protocols.py` | `receive_message()` | 429-443 |
| 发送完整请求 | `protocols/protocols.py` | `full_client_request()` | 460-467 |
| TTS 主流程 | `examples/volcengine/binary.py` | `main()` | 21-110 |
| ASR 客户端类 | `asr/streaming_asr_demo.py` | `AsrWsClient` | 169-318 |
| ASR 请求构建 | `asr/streaming_asr_demo.py` | `construct_request()` | 198-226 |
| ASR 分段处理 | `asr/streaming_asr_demo.py` | `segment_data_processor()` | 268-303 |
| 响应解析 | `asr/streaming_asr_demo.py` | `parse_response()` | 111-156 |
| Token 认证 | `asr/streaming_asr_demo.py` | `token_auth()` | 247-248 |
| HMAC 签名认证 | `asr/streaming_asr_demo.py` | `signature_auth()` | 250-266 |

---

## 十、Skills 封装建议

### 10.1 建议的 Skill 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Skills 封装架构                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Skill: doubao-tts                         │   │
│  │  功能: 文本转语音                                                 │   │
│  │  输入参数:                                                        │   │
│  │    - text (必填): 要合成的文本                                    │   │
│  │    - voice_type (可选): 音色ID, 默认某个音色                      │   │
│  │    - encoding (可选): 输出格式 wav/mp3, 默认mp3                   │   │
│  │    - speed_ratio (可选): 语速 0.1-2, 默认1.0                      │   │
│  │  输出: 音频文件路径 或 base64 音频数据                            │   │
│  │  环境变量: DOUBAO_APPID, DOUBAO_TOKEN                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Skill: doubao-asr                         │   │
│  │  功能: 语音转文本 (一句话识别)                                     │   │
│  │  输入参数:                                                        │   │
│  │    - audio_path (必填): 音频文件路径                              │   │
│  │    - format (可选): 音频格式 wav/mp3, 默认wav                     │   │
│  │    - language (可选): 语言, 默认 zh-CN                           │   │
│  │    - show_utterances (可选): 是否返回分句, 默认false              │   │
│  │  输出: 识别文本结果 (JSON)                                        │   │
│  │  环境变量: DOUBAO_APPID, DOUBAO_TOKEN, DOUBAO_CLUSTER            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     共享模块: doubao-core                         │   │
│  │  • DoubaoConfig - 配置管理类                                      │   │
│  │  • DoubaoProtocol - 二进制协议封装                                │   │
│  │  • DoubaoAuth - 认证处理                                          │   │
│  │  • DoubaoError - 统一异常类                                       │   │
│  │  • 错误码映射和处理                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 封装要点

1. **配置统一管理**: 使用环境变量或配置文件管理 appid/token
2. **错误处理标准化**: 统一的异常类和错误码映射
3. **接口简化**: 隐藏 WebSocket 连接细节，提供简单的同步/异步接口
4. **类型安全**: 使用 Pydantic 或 dataclass 定义参数模型
5. **日志记录**: 记录请求 ID 和 logid 便于问题追踪

### 10.3 示例接口设计

```python
# TTS Skill 接口设计
async def text_to_speech(
    text: str,
    voice_type: str = "zh_female_cancan_mars_bigtts",
    encoding: str = "mp3",
    speed_ratio: float = 1.0,
    output_path: Optional[str] = None
) -> Union[bytes, str]:
    """
    文本转语音

    Args:
        text: 要合成的文本
        voice_type: 音色ID
        encoding: 输出格式
        speed_ratio: 语速
        output_path: 输出文件路径，如果提供则保存文件并返回路径

    Returns:
        如果 output_path 为 None，返回音频 bytes
        否则返回保存的文件路径
    """
    pass

# ASR Skill 接口设计
async def speech_to_text(
    audio_path: str,
    format: str = "wav",
    language: str = "zh-CN",
    show_utterances: bool = False,
    enable_itn: bool = True,
    enable_punctuation: bool = True
) -> dict:
    """
    语音转文本

    Args:
        audio_path: 音频文件路径
        format: 音频格式
        language: 语言
        show_utterances: 是否返回分句信息
        enable_itn: 启用 ITN
        enable_punctuation: 启用标点

    Returns:
        识别结果 dict，包含 text, utterances 等
    """
    pass
```

---

## 附录

### A. 常见音色列表

| 音色ID | 说明 |
|--------|------|
| `zh_female_cancan_mars_bigtts` | 女声-灿灿 |
| `zh_male_M392_conversation_wvae_bigtts` | 男声对话 |
| `BV001_streaming` | 通用女声 |
| `BV002_streaming` | 通用男声 |

### B. 参考文档

- [火山引擎语音合成文档](https://www.volcengine.com/docs/6561/1257584)
- [火山引擎一句话识别文档](https://www.volcengine.com/docs/6561/80816)
- 项目内文档: `voice.md`, `asr.md`

---

*文档版本: 1.0*
*最后更新: 2026-02-07*
