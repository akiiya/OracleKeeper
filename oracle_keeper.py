import gc
import os
import random
import threading
import time
import codecs
import traceback

import urllib3
from io import BytesIO
from configparser import ConfigParser

# conf_file_path = 'conf/config.ini'
# pid_file_path = 'conf/oracle_keeper.pid'

pid_file_path = '/var/run/oracle_keeper.pid'
conf_file_path = '/etc/oracle_keeper/config.ini'

download_url_path = 'http://cachefly.cachefly.net/100mb.test'

mem_file = BytesIO()


# 保存当前进程pid
def save_pid():
    with codecs.open(pid_file_path, 'wb', encoding='utf-8') as f:
        f.write(str(os.getpid()))


# 读取之前的pid
def read_pid():
    if os.path.exists(pid_file_path):
        with codecs.open(pid_file_path, 'rb', encoding='utf-8') as f:
            return f.read()
    else:
        return None


# 读取配置文件
def read_conf():
    conf = ConfigParser()  # 需要实例化一个ConfigParser对象
    if not os.path.exists(conf_file_path):
        conf.add_section('cpu')
        conf.set('cpu', 'enable', '1')
        conf.set('cpu', 'round_count', '3600')  # 每一轮执行次数
        conf.set('cpu', 'interval_hour', '2')
        conf.set('cpu', 'interval_minute', '0')
        conf.set('cpu', 'interval_second', '0')

        conf.add_section('net')
        conf.set('net', 'enable', '1')
        conf.set('net', 'interval_hour', '2')
        conf.set('net', 'interval_minute', '0')
        conf.set('net', 'interval_second', '0')
        conf.set('net', 'max_speed_mb', '10')  # 下载限速
        conf.set('net', 'round_size_gb', '3')  # 每一轮下载的数据总量GB

        conf.add_section('mem')
        conf.set('mem', 'enable', '1')
        conf.set('mem', 'memory_gb', '3')

        conf_root = os.path.dirname(conf_file_path)

        if not os.path.exists(conf_root):
            os.makedirs(conf_root)

        with codecs.open(conf_file_path, "wb", encoding=u'utf-8-sig') as fp:
            conf.write(fp)
    else:
        with codecs.open(conf_file_path, "rb", encoding=u'utf-8-sig') as fp:
            conf.read_file(fp)
    return conf


# 消耗内存资源
def mem_consume(memory_gb, **kwargs):
    print(f'开始填充内存: {memory_gb}GB')
    while True:
        # 消耗内存
        if mem_file.tell() < memory_gb * 1024 * 1024 * 1024:
            mem_file.write(b'0' * 1024)
        else:
            break
    print(f'内存填充完成: {memory_gb}GB')


# 消耗cpu资源,计算斐波那契数列
def cpu_consume(interval, **kwargs):
    def sum_fibonacci(n=None):
        t1 = time.time()
        if not n:
            n = random.randint(180000, 240000)
        n1, n2 = 0, 1
        count = 0
        while count < n:
            n3 = n1 + n2
            n1 = n2
            n2 = n3
            count += 1
        tx = time.time() - t1

        if tx < 1:  # 耗时不足1秒补齐1秒
            time.sleep(1 - tx)

    round_count = None

    while True:
        # 计数没有结束需要继续消耗
        if round_count is None:
            print(f'开始本轮cpu消耗')
            round_count = kwargs.get('round_count', 60 * 60)
        elif round_count > 0:
            sum_fibonacci()
            round_count -= 1
        else:
            print(f'本轮cpu消耗结束')
            time.sleep(interval)
            round_count = None


# 消耗网络资源,下载文件
def net_consume(interval, **kwargs):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    max_speed_mb = kwargs.get('max_speed_mb', 10)
    round_size_gb = kwargs.get('round_size_gb', 3)
    timeout = urllib3.Timeout(connect=20, read=30)
    manager = urllib3.PoolManager(timeout=timeout, headers=headers)
    round_size = round_size_gb * 1000 * 1000 * 1000

    download_size = None

    while True:
        if download_size is None:
            print(f'开始本轮下载,共计 : {round_size_gb}GB')
            download_size = 0

        if round_size <= download_size:
            print(f'本轮下载完成,共计 : {round_size_gb}GB')
            time.sleep(interval)
            download_size = None

        try:
            response = manager.request('GET', download_url_path, preload_content=False)
            last_timestamp = time.time()

            while True:
                chunk = response.read(max_speed_mb * 1000 * 1000)

                if not chunk:
                    break

                shape_time = time.time() - last_timestamp

                if shape_time < 1:
                    time.sleep(1 - shape_time)

                download_size += len(chunk)
                del chunk
                gc.collect()

                last_timestamp = time.time()

            response.release_conn()
        except:
            traceback.print_exc()
            time.sleep(3)


# 关闭之前的进程,保存新进程
def close_older():
    old_pid = read_pid()
    if old_pid:
        os.system("kill -9 " + old_pid)
    save_pid()


def main_consume():
    close_older()
    conf = read_conf()

    mem_enable = conf.getint('mem', 'enable')
    memory_gb = conf.getint('mem', 'memory_gb')

    cpu_enable = conf.getint('cpu', 'enable')
    cpu_round_count = conf.getint('cpu', 'round_count')
    cpu_interval_hour = conf.getint('cpu', 'interval_hour')
    cpu_interval_minute = conf.getint('cpu', 'interval_minute')
    cpu_interval_second = conf.getint('cpu', 'interval_second')

    net_enable = conf.getint('net', 'enable')
    net_max_speed_mb = conf.getint('net', 'max_speed_mb')  # 限速每秒
    net_round_size_gb = conf.getint('net', 'round_size_gb')  # 每轮下载数据总量
    net_interval_hour = conf.getint('net', 'interval_hour')
    net_interval_minute = conf.getint('net', 'interval_minute')
    net_interval_second = conf.getint('net', 'interval_second')

    cpu_interval = cpu_interval_hour * 60 * 60 + cpu_interval_minute * 60 + cpu_interval_second
    net_interval = net_interval_hour * 60 * 60 + net_interval_minute * 60 + net_interval_second

    if mem_enable:
        threading.Thread(
            target=mem_consume,
            kwargs={
                'memory_gb': memory_gb
            }
        ).start()

    if cpu_enable:
        threading.Thread(
            target=cpu_consume,
            kwargs={
                'interval': cpu_interval,
                'round_count': cpu_round_count,
            }
        ).start()

    if net_enable:
        threading.Thread(
            target=net_consume,
            kwargs={
                'interval': net_interval,
                'max_speed_mb': net_max_speed_mb,
                'round_size_gb': net_round_size_gb
            }
        ).start()

    while True:
        time.sleep(60 * 60 * 24)


def test_consume():
    # cpu_consume(100, round_count=10)
    net_consume(100, round_size_gb=1, max_speed_mb=100)
    # mem_consume(2)
    exit()


if __name__ == '__main__':
    main_consume()
