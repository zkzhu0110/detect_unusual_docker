#!/bin/env python
#encoding=utf-8

import os
import paramiko
from functools import wraps
from datetime import datetime


def timethis(func):
    """
    时间装饰器，计算函数执行所消耗的时间
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        print(func.__name__, end - start)
        return result

    return wrapper

class SFTPManager:
    def __init__(self, host, usr, passwd, port=22):
        self._host = host
        self._port = port
        self._usr = usr
        self._passwd = passwd
        self._sftp = None
        self._sftp_connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __del__(self):
        if self._sftp:
            self._sftp.close()

    def _sftp_connect(self):
        try:
            transport = paramiko.Transport((self._host, self._port))
            transport.connect(username=self._usr, password=self._passwd)
            self._sftp = paramiko.SFTPClient.from_transport(transport)
        except Exception as e:
            raise RuntimeError("sftp connect failed {}".format(str(e)))

    @timethis
    def _upload_file(self, local_file, remote_file):
        """
        通过sftp上传本地文件到远程
        :param local_file:
        :param remote_file:
        :return:
        """
        try:
            self._sftp.put(local_file, remote_file)
        except Exception as e:
            raise RuntimeError('upload failed [{}]'.format(str(e)))

class SSHManager:
    def __init__(self, host, usr, passwd, port=22):
        self._host = host
        self._port = port
        self._usr = usr
        self._passwd = passwd
        self._ssh = None
        self._ssh_connect()

    def ssh_close(self):
        self.__del__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __del__(self):
        if self._ssh:
            self._ssh.close()

    def _ssh_connect(self):
        try:
            # 创建ssh对象
            self._ssh = paramiko.SSHClient()
            # 允许连接不在know_hosts文件中的主机
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接服务器
            self._ssh.connect(hostname=self._host,
                              port=self._port,
                              username=self._usr,
                              password=self._passwd,
                              timeout=10)
        except Exception:
            raise RuntimeError("ssh connected to [host:{}, port:{} usr:{}] failed".format\
                               (self._host, self._port, self._usr))

    def ssh_exec_cmd(self, cmd, sudo=False):
        """
        通过ssh连接到远程服务器，执行给定的命令
        :param cmd: 执行的命令
        :param path: 命令执行的目录
        :return: 返回结果
        """
        try:
            return self._exec_command(cmd, sudo)
        except Exception:
            raise RuntimeError('exec cmd [%s] failed' % cmd)

    @staticmethod
    def is_shell_file(file_name):
        return file_name.endswith('.sh')

    @staticmethod
    def is_file_exist(file_name):
        try:
            with open(file_name, 'r'):
                return True
        except Exception as e:
            return False

    def _exec_command(self, cmd, sudo=False):
        """
        通过ssh执行远程命令
        :param cmd:
        :return:
        """
        try:
            if sudo:
                cmd = cmd.replace('sudo', 'sudo -S ')
            stdin, stdout, stderr = self._ssh.exec_command(cmd)
            print('------')
            if sudo:
                stdin.write(self._passwd + '\n')
                stdin.flush()
            channel = stdout.channel
            status = channel.recv_exit_status()

            return dict(status = status, stdout = stdout.read().decode('utf-8'),
                        stderr = stderr.read().decode('utf-8'))
        except Exception as e:
            raise RuntimeError('Exec command [{}] failed'.format(str(cmd)))


if __name__ == '__main__':
    ip = '10.10.8.5'
    usr = 'leinao'
    passwd = '12345678'
    ssh = SSHManager(ip, usr, passwd)
    ssh.ssh_exec_cmd('sudo docker ps ', sudo = True)
    print(ssh.ssh_exec_cmd('ls hh', sudo = True))
    #ssh.ssh_exec_shell('./test.sh', '/home/leo/test.sh', '/home/leo')
