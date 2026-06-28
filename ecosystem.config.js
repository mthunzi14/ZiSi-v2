module.exports = {
  apps: [
    {
      name: 'ZiSi-Core-Engine',
      script: '/root/ZiSi-v2/venv/bin/python3',
      args: 'app/main.py',
      cwd: '/root/ZiSi-v2',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '800M',
      env: { PYTHONPATH: '/root/ZiSi-v2' }
    }
  ]
};

