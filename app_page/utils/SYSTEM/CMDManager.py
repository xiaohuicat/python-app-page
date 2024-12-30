import subprocess

class CMDManager:
    def __init__(self,LIVE) -> None:
        self.isSteam = True
        self.LIVE = LIVE
        self.encoding = "utf-8"

    def run_command(self, command):
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True, text=True)
            # 如果命令成功执行，可以通过 result.stdout 获取标准输出
            return result.stdout
        except subprocess.CalledProcessError as e:
            # 如果命令执行失败，可以通过 e.stderr 获取错误信息
            return f"Error: {e.stderr}"
        
    def run_streaming_command(self, command):
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, encoding=self.encoding)

            # 逐行读取输出
            for line in process.stdout:
                # print(line.strip())
                ret = (">>>"+line).strip().replace('>>>','')
                # print(ret)
                self.LIVE and self.LIVE["success"](ret)

            # 等待进程结束
            process.wait()

            # 获取错误信息（如果有的话）
            errors = process.stderr.read()
            if errors:
                print(f"Error: {errors}")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.LIVE and self.LIVE["error"](f"An error occurred: {e}")

    def run(self, cmd_command):
        self.LIVE and self.LIVE["before"]()
        if self.isSteam:
            self.run_streaming_command(cmd_command)
            self.LIVE and self.LIVE["finish"]("运行结束")
        else:
            ret = self.run_command(cmd_command)
            self.LIVE and self.LIVE["finish"](ret)

# run_streaming_command("cd ./前端开发项目/server/greatnote_server && node main")