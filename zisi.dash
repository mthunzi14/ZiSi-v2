#!/bin/bash
# Tmux persistent runner for ZiSi-v2 Terminal Dashboard
SESSION="zisi"

# Check if session already exists
tmux has-session -t $SESSION 2>/dev/null

if [ $? -ne 0 ]; then
  # Session does not exist, create it and run the dashboard
  echo "Starting new persistent dashboard session..."
  tmux new-session -d -s $SESSION "/root/ZiSi-v2/venv/bin/python3 /root/ZiSi-v2/zisi_terminal.py"
else
  echo "Attaching to existing persistent dashboard session..."
fi

# Attach to the session
tmux attach -t $SESSION
