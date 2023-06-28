import requests
import time
import os


# 从环境变量中读取主控端地址和端口以及节点验证密钥
CONTROLLER_HOST = os.environ.get('CONTROLLER_HOST')
CONTROLLER_PORT = os.environ.get('CONTROLLER_PORT')
NODEID_KEY = os.environ.get('NODEID_KEY')

# 获取本机的外网IPv4地址
def get_public_ipv4():
    response = requests.get('https://api.ipify.org?format=json')
    if response.status_code == 200:
        return response.json()['ip']
    else:
        raise Exception('Failed to retrieve public IPv4 address')

# 爬虫节点标识
NODE_ID = get_public_ipv4()

# 爬虫节点待机状态
is_idle = True

# 循环接收任务并执行
while True:
    try:
        if is_idle:
            # 爬虫节点处于待机状态，向主控端请求任务
            response = requests.get(f"http://{CONTROLLER_HOST}:{CONTROLLER_PORT}/assign_task?node_id={NODE_ID}&node_id_key={NODEID_KEY}")
            if response.status_code == 200:
                # 成功接收到任务
                task = response.json()
                task_id = task['task_id']
                url = task['url']

                # 执行爬取任务
                response = requests.get(url)
                if response.status_code == 200:
                    # 将页面内容回传给主控端
                    data = response.text
                    requests.post(f"http://{CONTROLLER_HOST}:{CONTROLLER_PORT}/submit_result",
                                  json={"task_id": task_id, "node_id_key" : NODEID_KEY, "data": data})
                else:
                    # 请求页面失败，将任务标记为失败
                    requests.post(f"http://{CONTROLLER_HOST}:{CONTROLLER_PORT}/mark_task_failed",
                                  json={"task_id": task_id, "node_id_key" : NODEID_KEY,})
            else:
                # 没有任务可分配，继续等待
                time.sleep(1)
        else:
            # 爬虫节点不处于待机状态，等待主控端重新连接
            response = requests.get(f"http://{CONTROLLER_HOST}:{CONTROLLER_PORT}/heartbeat?node_id={NODE_ID}")
            if response.status_code != 200:
                # 主控端失联，爬虫节点保持待机状态
                is_idle = True
                time.sleep(1)
    except requests.exceptions.RequestException:
        # 发生网络异常，等待一段时间后重试
        time.sleep(1)
