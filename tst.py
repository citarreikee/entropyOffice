import subprocess
import platform

def ping_ip(ip_address):
    """
    Pings the given IP address and returns whether it is reachable.
    """
    # Determine the OS and set the appropriate ping command
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # Build the ping command
    command = ['ping', param, '1', ip_address]
    
    try:
        # Run the ping command
        response = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        # If response is 0, the host is reachable
        return response == 0
    except Exception as e:
        print(f"发生错误: {e}")
        return False

if __name__ == "__main__":
    ip = input("请输入要 ping 的 IP 地址：")
    print(f"正在 ping {ip} ...")

    if ping_ip(ip):
        print("✅ 设备在线")
    else:
        print("❌ 设备不在线")