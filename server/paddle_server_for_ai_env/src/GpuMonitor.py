import pynvml
import subprocess
import time
import psutil

pynvml.nvmlInit()
gpuCount = pynvml.nvmlDeviceGetCount()
while True:
    for gpuIndex in range(gpuCount):
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpuIndex)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        totalMem = meminfo.total
        usedMen = meminfo.used
        print("GPU" + str(gpuIndex) + " mem info：")
        print("\ttotal mem：" + str(totalMem / 1024 ** 2))  # 总的显存大小（float）
        print("\tused mem：" + str(usedMen / 1024 ** 2))  # 已用显存大小（float）
        print("\tfree mem：" + str(meminfo.free / 1024 ** 2))  # 剩余显存大小（float）
        if usedMen / totalMem >= 0.85:
            print("GPU" + str(gpuIndex) + " memory used more than 85%, kill ai programs running in this GPU")
            programs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
            # kill program
            for program in programs:
                p = psutil.Process(program.pid)
                print(p.name())
                if not str(p.name()).lower().startswith("python3"):
                    continue
                print("to kill program pid:" + str(program.pid))
                output = subprocess.Popen(
                    "kill -9 " + str(program.pid),
                    stdout=subprocess.PIPE,
                    shell=True
                ).communicate()[0].decode()
                print(output)
    # 每20秒监控一次，释放paddle进程占用的显存（貌似paddlepaddle只有进程退出才会释放显存）
    time.sleep(20)