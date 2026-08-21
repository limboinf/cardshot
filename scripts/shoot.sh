#!/bin/bash
# shoot.sh — cardshot 出图封装 (相对本仓库, clone 到哪都能跑)
# 用法:
#   shoot.sh auto                    # 按各卡自带尺寸出图 (最常用)
#   shoot.sh presets xhs douyin      # 指定平台预设批量
#   shoot.sh all                     # 每张卡 × 全部预设
#   shoot.sh one cards/foo.html -p xhs   # 单卡单预设
#   shoot.sh <任意 shooter.py 参数>      # 透传
set -euo pipefail

# 定位脚本所在目录的上一级 = 仓库根 (兼容 macOS/BSD readlink 无 -f)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$SCRIPT_DIR")"
SHOOTER="$REPO/shooter.py"

[ -f "$SHOOTER" ] || { echo "未找到 $SHOOTER"; exit 1; }

mode="${1:-}"
shift || true

case "$mode" in
  auto)    exec python3 "$SHOOTER" "$REPO/cards/" --auto "$@" ;;
  all)     exec python3 "$SHOOTER" "$REPO/cards/" --all-presets "$@" ;;
  presets) exec python3 "$SHOOTER" "$REPO/cards/" -p "$@" ;;
  one)     exec python3 "$SHOOTER" "$@" ;;
  *)       exec python3 "$SHOOTER" "$mode" "$@" ;;
esac
