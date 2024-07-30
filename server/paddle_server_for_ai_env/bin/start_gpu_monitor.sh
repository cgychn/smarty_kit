source /opt/ai_env/bin/activate
export LD_LIBRARY_PATH=/opt/ai_env/lib:/opt/ai_env/include:/usr/local/cuda-12.1/lib64:/usr/local/cuda-12.1/include
cd /opt/paddle_server_for_ai_env/src
python3 -u GpuMonitor.py
