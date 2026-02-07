#!/usr/bin/env bash
#
# Doubao Speech Skills OpenClaw Installer
#
# 一键安装豆包语音服务 Skills 到 OpenClaw
# Installs doubao-tts and doubao-asr skills to ~/.openclaw/skills/
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/geekjourneyx/doubao-skills/main/scripts/install-openclaw.sh | bash
#

set -e

REPO="geekjourneyx/doubao-skills"
INSTALL_BASE="${HOME}/.openclaw/skills"
GITHUB_ARCHIVE="https://github.com/${REPO}/archive/refs/heads/main.tar.gz"

# Skills to install
SKILLS=("doubao-tts" "doubao-asr")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { printf "${BLUE}ℹ${NC} %s\n" "$1"; }
success() { printf "${GREEN}✓${NC} %s\n" "$1"; }
warn()    { printf "${YELLOW}⚠${NC} %s\n" "$1"; }
error()   { printf "${RED}✗${NC} %s\n" "$1" >&2; exit 1; }

# Header
printf "\n"
printf "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}\n"
printf "${CYAN}║       豆包语音服务 Skills 安装脚本                       ║${NC}\n"
printf "${CYAN}║       Doubao Speech Skills Installer                     ║${NC}\n"
printf "${CYAN}╠══════════════════════════════════════════════════════════╣${NC}\n"
printf "${CYAN}║  🎙️  doubao-tts  - 语音合成 (Text-to-Speech)             ║${NC}\n"
printf "${CYAN}║  🎧  doubao-asr  - 语音识别 (Speech-to-Text)             ║${NC}\n"
printf "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}\n"
printf "\n"

# Check for npx skills first
if command -v npx &>/dev/null; then
    info "检测到 npx，推荐使用 npx skills 安装"
    info "Detected npx, recommend using npx skills"
    printf "\n"
    printf "  ${GREEN}npx skills add ${REPO}${NC}\n"
    printf "\n"
    read -p "继续手动安装？/ Continue manual install? [y/N] " -n 1 -r
    printf "\n"
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
fi

# Check prerequisites
command -v curl &>/dev/null || command -v wget &>/dev/null || \
    error "需要 curl 或 wget / Need curl or wget"

command -v tar &>/dev/null || \
    error "需要 tar / Need tar"

# Check Python
if ! command -v python3 &>/dev/null; then
    warn "未检测到 Python3 / Python3 not detected"
    info "请先安装 Python 3.9+ / Install Python 3.9+ first"
fi

# Check if OpenClaw directory exists
if [[ ! -d "${HOME}/.openclaw" ]]; then
    warn "未检测到 OpenClaw 安装 / OpenClaw not detected"
    info "将创建目录 / Will create directory: ~/.openclaw/skills/"
    printf "\n"
    read -p "继续安装？/ Continue? [Y/n] " -n 1 -r
    printf "\n"
    [[ $REPLY =~ ^[Nn]$ ]] && exit 0
    mkdir -p "${HOME}/.openclaw"
fi

# Check for existing installations
EXISTING=""
for skill in "${SKILLS[@]}"; do
    if [[ -d "${INSTALL_BASE}/${skill}" ]]; then
        EXISTING="${EXISTING} ${skill}"
    fi
done

if [[ -n "$EXISTING" ]]; then
    warn "检测到已安装的 Skills / Existing installations:${EXISTING}"
    read -p "覆盖安装？/ Overwrite? [y/N] " -n 1 -r
    printf "\n"
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
    for skill in "${SKILLS[@]}"; do
        rm -rf "${INSTALL_BASE}/${skill}" 2>/dev/null || true
    done
fi

# Download and extract
info "下载 Skills 文件 / Downloading skill files..."

TEMP_DIR=$(mktemp -d)
ARCHIVE="${TEMP_DIR}/repo.tar.gz"

cleanup() {
    rm -rf "$TEMP_DIR" 2>/dev/null || true
}
trap cleanup EXIT

if command -v curl &>/dev/null; then
    curl -fsSL "$GITHUB_ARCHIVE" -o "$ARCHIVE" || error "下载失败 / Download failed"
else
    wget -q "$GITHUB_ARCHIVE" -O "$ARCHIVE" || error "下载失败 / Download failed"
fi

tar -xzf "$ARCHIVE" -C "$TEMP_DIR" || error "解压失败 / Extract failed"

# Find extracted directory
EXTRACTED=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "doubao-skills-*" | head -n 1)
[[ -z "$EXTRACTED" ]] && error "找不到解压目录 / Cannot find extracted directory"

# Install skills
info "安装 Skills / Installing skills..."

mkdir -p "$INSTALL_BASE"

for skill in "${SKILLS[@]}"; do
    if [[ -d "${EXTRACTED}/skills/${skill}" ]]; then
        cp -r "${EXTRACTED}/skills/${skill}" "${INSTALL_BASE}/"
        chmod +x "${INSTALL_BASE}/${skill}/scripts/"*.py 2>/dev/null || true
        success "已安装 / Installed: ${skill}"
    else
        warn "未找到 / Not found: ${skill}"
    fi
done

success "安装完成 / Installation complete!"

# Check Python dependencies
printf "\n"
printf "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
printf "${BLUE}   检查依赖 / Checking Dependencies${NC}\n"
printf "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
printf "\n"

MISSING_DEPS=""

if python3 -c "import requests" 2>/dev/null; then
    success "requests 已安装"
else
    MISSING_DEPS="${MISSING_DEPS} requests"
    warn "requests 未安装"
fi

if python3 -c "import websockets" 2>/dev/null; then
    success "websockets 已安装"
else
    MISSING_DEPS="${MISSING_DEPS} websockets"
    warn "websockets 未安装"
fi

if [[ -n "$MISSING_DEPS" ]]; then
    printf "\n"
    info "请安装缺失的依赖 / Install missing dependencies:"
    printf "  ${GREEN}pip install${MISSING_DEPS}${NC}\n"
fi

# Configuration instructions
printf "\n"
printf "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
printf "${BLUE}   配置说明 / Configuration${NC}\n"
printf "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
printf "\n"

printf "${YELLOW}第一步 / Step 1: 设置环境变量${NC}\n"
printf "\n"
printf "  ${GREEN}export DOUBAO_APPID=\"your-appid\"${NC}\n"
printf "  ${GREEN}export DOUBAO_TOKEN=\"your-access-token\"${NC}\n"
printf "  ${GREEN}export DOUBAO_CLUSTER=\"your-cluster\"${NC}  # ASR 必需\n"
printf "\n"

CONFIG_FILE="${HOME}/.openclaw/openclaw.json"

printf "${YELLOW}第二步 / Step 2: 配置 OpenClaw (可选)${NC}\n"
printf "\n"

if [[ -f "$CONFIG_FILE" ]]; then
    printf "检测到配置文件 / Config found: ${GREEN}${CONFIG_FILE}${NC}\n"
    printf "\n"
    printf "请在 skills.entries 中添加:\n"
    printf "\n"
else
    printf "创建配置文件 / Create config: ${GREEN}${CONFIG_FILE}${NC}\n"
    printf "\n"
fi

printf "${GREEN}"
cat << 'EOF'
{
  "skills": {
    "entries": {
      "doubao-tts": {
        "enabled": true,
        "env": {
          "DOUBAO_APPID": "your-appid",
          "DOUBAO_TOKEN": "your-token"
        }
      },
      "doubao-asr": {
        "enabled": true,
        "env": {
          "DOUBAO_APPID": "your-appid",
          "DOUBAO_TOKEN": "your-token",
          "DOUBAO_CLUSTER": "your-cluster"
        }
      }
    }
  }
}
EOF
printf "${NC}\n"

# Summary
printf "\n"
printf "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
printf "${BLUE}   安装信息 / Installation Info${NC}\n"
printf "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
printf "\n"
printf "安装路径 / Installed to:\n"
for skill in "${SKILLS[@]}"; do
    if [[ -d "${INSTALL_BASE}/${skill}" ]]; then
        printf "  ${GREEN}${INSTALL_BASE}/${skill}${NC}\n"
    fi
done
printf "\n"
printf "获取凭证 / Get credentials:\n"
printf "  ${CYAN}https://console.volcengine.com/speech/service/8${NC}\n"
printf "\n"
printf "项目文档 / Documentation:\n"
printf "  ${CYAN}https://github.com/${REPO}#readme${NC}\n"
printf "\n"
printf "火山引擎文档 / Volcano Engine Docs:\n"
printf "  TTS: ${CYAN}https://www.volcengine.com/docs/6561/1257584${NC}\n"
printf "  ASR: ${CYAN}https://www.volcengine.com/docs/6561/80816${NC}\n"
printf "\n"

success "重启 OpenClaw 或 Claude Code 后生效"
success "Restart OpenClaw or Claude Code to load skills"
printf "\n"
