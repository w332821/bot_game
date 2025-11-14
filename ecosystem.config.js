/**
 * PM2 配置文件
 *
 * 使用方法：
 * - 启动Python版本: pm2 start ecosystem.config.js --only game-bot-python
 * - 启动Node.js版本: pm2 start ecosystem.config.js --only game-bot-nodejs
 * - 同时启动两个: pm2 start ecosystem.config.js
 *
 * 注意：Python和Node.js版本不要同时运行（端口冲突）
 */

module.exports = {
  apps: [
    // Python 版本（新版本，推荐使用）
    {
      name: 'game-bot-python',
      script: './start_bot.sh',
      interpreter: 'bash',
      cwd: '/root/bot_game/bot_game',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: '/root/.pm2/logs/game-bot-python-error.log',
      out_file: '/root/.pm2/logs/game-bot-python-out.log',
      time: true,
      merge_logs: true
    },

    // Node.js 版本（旧版本，仅供参考）
    {
      name: 'game-bot-nodejs',
      script: 'bot-server.js',
      cwd: '/root/bot_game/bot_game/game-bot-master',
      interpreter: 'node',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: '/root/.pm2/logs/game-bot-nodejs-error.log',
      out_file: '/root/.pm2/logs/game-bot-nodejs-out.log',
      time: true,
      merge_logs: true
    }
  ]
};
