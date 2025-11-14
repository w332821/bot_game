#!/usr/bin/env python3
"""
验证 Python Bot 修复的完整性
检查所有可能导致运行时错误的问题
"""

import ast
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class CodeVerifier:
    """代码验证器"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg: str):
        """记录错误"""
        self.errors.append(f"❌ {msg}")
        print(f"❌ {msg}")

    def warning(self, msg: str):
        """记录警告"""
        self.warnings.append(f"⚠️  {msg}")
        print(f"⚠️  {msg}")

    def success(self, msg: str):
        """记录成功"""
        print(f"✅ {msg}")

    def check_file_exists(self, filepath: str) -> bool:
        """检查文件是否存在"""
        path = project_root / filepath
        if not path.exists():
            self.error(f"文件不存在: {filepath}")
            return False
        return True

    def check_method_exists(self, filepath: str, class_name: str, method_name: str) -> bool:
        """检查类方法是否存在"""
        path = project_root / filepath
        if not path.exists():
            return False

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == method_name:
                            return True
            return False
        except Exception as e:
            self.warning(f"解析文件失败 {filepath}: {e}")
            return False

    def check_import_exists(self, filepath: str, module: str) -> bool:
        """检查导入是否存在"""
        path = project_root / filepath
        if not path.exists():
            return False

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return module in content
        except Exception as e:
            self.warning(f"读取文件失败 {filepath}: {e}")
            return False

    def verify_all(self):
        """执行所有验证"""
        print("\n" + "="*60)
        print("开始验证 Python Bot 代码完整性")
        print("="*60 + "\n")

        # 1. 检查关键文件存在
        print("\n【1】检查关键文件...")
        critical_files = [
            'biz/chat/repo/chat_repo.py',
            'biz/game/webhook/webhook_api.py',
            'external/bot_api_client.py',
            'biz/game/service/game_service.py',
            'biz/user/repo/user_repo.py',
            'biz/game/logic/game_logic.py',
        ]

        all_files_exist = True
        for filepath in critical_files:
            if self.check_file_exists(filepath):
                self.success(f"文件存在: {filepath}")
            else:
                all_files_exist = False

        if not all_files_exist:
            self.error("关键文件缺失，无法继续验证")
            return

        # 2. 检查 ChatRepository 方法
        print("\n【2】检查 ChatRepository 方法...")
        required_methods = ['get_by_id', 'get_chat', 'create_chat', 'update_chat']
        for method in required_methods:
            if self.check_method_exists('biz/chat/repo/chat_repo.py', 'ChatRepository', method):
                self.success(f"ChatRepository.{method}() 存在")
            else:
                self.error(f"ChatRepository.{method}() 不存在")

        # 3. 检查 BotApiClient 认证方法
        print("\n【3】检查 BotApiClient 认证方法...")
        bot_api_methods = ['_generate_signature', '_get_headers', 'send_message', 'join_chat', 'send_image']
        for method in bot_api_methods:
            if self.check_method_exists('external/bot_api_client.py', 'BotApiClient', method):
                self.success(f"BotApiClient.{method}() 存在")
            else:
                self.error(f"BotApiClient.{method}() 不存在")

        # 4. 检查认证头字段
        print("\n【4】检查 Bot API 认证实现...")
        bot_api_path = project_root / 'external/bot_api_client.py'
        with open(bot_api_path, 'r', encoding='utf-8') as f:
            bot_api_content = f.read()

        if 'X-API-Key' in bot_api_content:
            self.success("使用 X-API-Key 认证头")
        else:
            self.error("缺少 X-API-Key 认证头")

        if 'X-Signature' in bot_api_content:
            self.success("使用 X-Signature 认证头")
        else:
            self.error("缺少 X-Signature 认证头")

        if 'X-Timestamp' in bot_api_content:
            self.success("使用 X-Timestamp 认证头")
        else:
            self.error("缺少 X-Timestamp 认证头")

        if 'hmac' in bot_api_content and 'hashlib' in bot_api_content:
            self.success("使用 HMAC-SHA256 签名")
        else:
            self.error("缺少 HMAC-SHA256 签名实现")

        # 5. 检查 webhook_api.py 中的方法调用
        print("\n【5】检查 webhook_api.py 方法调用...")
        webhook_path = project_root / 'biz/game/webhook/webhook_api.py'
        with open(webhook_path, 'r', encoding='utf-8') as f:
            webhook_content = f.read()

        # 检查是否使用正确的方法名
        if 'chat_repo.create(' in webhook_content:
            self.error("webhook_api.py 使用了错误的方法名 chat_repo.create()")
        else:
            self.success("webhook_api.py 没有使用错误的 chat_repo.create()")

        if 'chat_repo.create_chat(' in webhook_content:
            self.success("webhook_api.py 正确使用 chat_repo.create_chat()")
        else:
            self.error("webhook_api.py 缺少 chat_repo.create_chat() 调用")

        if 'chat_repo.get_by_id(' in webhook_content:
            self.success("webhook_api.py 正确使用 chat_repo.get_by_id()")
        else:
            self.error("webhook_api.py 缺少 chat_repo.get_by_id() 调用")

        # 6. 检查 UserRepository 方法
        print("\n【6】检查 UserRepository 方法...")
        user_repo_methods = [
            'get_user_in_chat',
            'create_user',
            'add_balance',
            'subtract_balance',
            'get_chat_users',
        ]
        for method in user_repo_methods:
            if self.check_method_exists('biz/user/repo/user_repo.py', 'UserRepository', method):
                self.success(f"UserRepository.{method}() 存在")
            else:
                self.error(f"UserRepository.{method}() 不存在")

        # 7. 检查环境变量配置
        print("\n【7】检查环境变量配置...")
        env_path = project_root / '.env'
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.read()

            if 'BOT_API_KEY=' in env_content:
                self.success(".env 包含 BOT_API_KEY")
            else:
                self.warning(".env 缺少 BOT_API_KEY")

            if 'BOT_API_SECRET=' in env_content:
                self.success(".env 包含 BOT_API_SECRET")
            else:
                self.warning(".env 缺少 BOT_API_SECRET")

            if 'BOT_API_BASE=' in env_content:
                self.success(".env 包含 BOT_API_BASE")
            else:
                self.warning(".env 缺少 BOT_API_BASE")
        else:
            self.warning(".env 文件不存在")

        # 8. 生成报告
        print("\n" + "="*60)
        print("验证完成")
        print("="*60)

        print(f"\n✅ 成功: {len([m for m in self.warnings if '✅' in m])}")
        print(f"⚠️  警告: {len(self.warnings)}")
        print(f"❌ 错误: {len(self.errors)}")

        if self.errors:
            print("\n❌ 发现以下错误:")
            for error in self.errors:
                print(f"  {error}")
            return False
        elif self.warnings:
            print("\n⚠️  发现以下警告:")
            for warning in self.warnings:
                print(f"  {warning}")
            return True
        else:
            print("\n✅ 所有检查通过！")
            return True


def main():
    """主函数"""
    verifier = CodeVerifier()
    success = verifier.verify_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
