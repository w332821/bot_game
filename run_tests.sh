#!/bin/bash
# 简单的测试运行脚本
set -e
echo "运行测试..."
python -m pytest tests/ -v
