#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1.6'

import click
import signal

from netkit.stream import Stream
from netkit.box import Box

import time
import socket
from multiprocessing import Process, Value
from threading import Thread


class WSClientStream(object):
    """
    websocket的封装
    """

    def __init__(self, sock):
        self.sock = sock

    def write(self, data):
        from websocket import ABNF
        return self.sock.send(data, ABNF.OPCODE_BINARY)

    def read_with_checker(self, *args, **kwargs):
        return self.sock.recv()

    def close(self, *args, **kwargs):
        return self.sock.close(*args, **kwargs)


class ProcessWorker(object):
    """
    进程worker
    """
    # 经过的时间
    elapsed_time = 0
    # 总请求，如果链接失败而没发送，不算在这里
    transactions = 0
    # 成功请求数
    successful_transactions = 0
    # 失败请求数，因为connect失败导致没发的请求也算在这里. 这3个值没有绝对的相等关系
    failed_transactions = 0

    def __init__(self, concurrent, reps, url, msg_cmd, socket_type, timeout, share_result):
        self.concurrent = concurrent
        self.reps = reps
        self.url = url
        self.msg_cmd = msg_cmd
        self.socket_type = socket_type
        self.timeout = timeout
        self.share_result = share_result
        self.stream_checker = Box().check

    def make_stream(self):
        if self.socket_type == 'socket':
            host, port = self.url.split(':')
            address = (host, int(port))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(address)
            s.settimeout(self.timeout)
            stream = Stream(s, use_gevent=True, lock_mode=0)
        else:
            import websocket
            s = websocket.create_connection(self.url)
            stream = WSClientStream(s)

        return stream

    def thread_worker(self, worker_idx):
        try:
            stream = self.make_stream()
        except:
            # 直接把所有的错误请求都加上
            self.failed_transactions += self.reps
            click.secho('thread_worker[%s] socket connect fail' % worker_idx, fg='red')
            return

        box = Box()
        box.cmd = self.msg_cmd

        send_buf = box.pack()
        for it in xrange(0, self.reps):
            self.transactions += 1
            stream.write(send_buf)
            try:
                recv_buf = stream.read_with_checker(self.stream_checker)
            except socket.timeout:
                self.failed_transactions += 1
                click.secho('thread_worker[%s] socket timeout' % worker_idx, fg='red')
                continue

            if not recv_buf:
                click.secho('thread_worker[%s] socket closed' % worker_idx, fg='red')
                self.failed_transactions += 1
                break
            else:
                self.successful_transactions += 1

    def run(self):
        self._handle_child_proc_signals()

        jobs = []

        begin_time = time.time()

        for it in xrange(0, self.concurrent):
            job = Thread(target=self.thread_worker, args=[it])
            job.daemon = True
            job.start()
            jobs.append(job)

        for job in jobs:
            job.join()

        end_time = time.time()

        self.elapsed_time = end_time - begin_time

        self.share_result['elapsed_time'].value += self.elapsed_time
        self.share_result['transactions'].value += self.transactions
        self.share_result['successful_transactions'].value += self.successful_transactions
        self.share_result['failed_transactions'].value += self.failed_transactions

    def _handle_child_proc_signals(self):
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

class Shock(object):

    # 经过的时间
    share_elapsed_time = Value('f', 0)
    # 总请求，如果链接失败而没发送，不算在这里
    share_transactions = Value('i', 0)
    # 成功请求数
    share_successful_transactions = Value('i', 0)
    # 失败请求数，因为connect失败导致没发的请求也算在这里. 这3个值没有绝对的相等关系
    share_failed_transactions = Value('i', 0)


    def __init__(self, concurrent, reps, url, msg_cmd, socket_type, timeout, process_count):
        self.concurrent = concurrent
        self.reps = reps
        self.url = url
        self.msg_cmd = msg_cmd
        self.socket_type = socket_type
        self.timeout = timeout
        self.process_count = process_count

    def run(self):
        self._handle_parent_proc_signals()

        worker = ProcessWorker(self.concurrent_per_process, self.reps, self.url, self.msg_cmd, self.socket_type, self.timeout, dict(
            elapsed_time=self.share_elapsed_time,
            transactions=self.share_transactions,
            successful_transactions=self.share_successful_transactions,
            failed_transactions=self.share_failed_transactions,
        ))

        jobs = []

        for it in xrange(0, self.process_count):
            job = Process(target=worker.run)
            job.daemon = True
            job.start()
            jobs.append(job)

        for job in jobs:
            job.join()

        # 平均
        self.share_elapsed_time.value = self.share_elapsed_time.value / self.process_count

    def _handle_parent_proc_signals(self):
        # 修改SIGTERM，否则父进程被term，子进程不会自动退出；明明子进程都设置为daemon了的
        signal.signal(signal.SIGTERM, signal.default_int_handler)
        # 即使对于SIGINT，SIG_DFL和default_int_handler也是不一样的，要是想要抛出KeyboardInterrupt，应该用default_int_handler
        signal.signal(signal.SIGINT, signal.default_int_handler)

    @property
    def elapsed_time(self):
        return self.share_elapsed_time.value

    @property
    def transactions(self):
        return self.share_transactions.value

    @property
    def successful_transactions(self):
        return self.share_successful_transactions.value

    @property
    def failed_transactions(self):
        return self.share_failed_transactions.value

    @property
    def transaction_rate(self):
        """
        每秒的请求数
        """
        if self.elapsed_time != 0:
            return 1.0 * self.transactions / self.elapsed_time
        else:
            return 0

    @property
    def response_time(self):
        """
        平均响应时间
        """
        if self.transactions != 0:
            return 1.0 * self.elapsed_time / self.transactions
        else:
            return 0

    @property
    def plan_transactions(self):
        """
        计划的请求数
        :return:
        """
        return self.concurrent * self.reps

    @property
    def availability(self):
        if self.plan_transactions != 0:
            return 1.0 * self.successful_transactions / self.plan_transactions
        else:
            return 0

    @property
    def concurrent_per_process(self):
        """
        每个进程需要启动的并发链接数
        :return:
        """
        return int(self.concurrent / self.process_count)


@click.command()
@click.option('--concurrent', '-c', type=int, default=10, help='spawn users, 10')
@click.option('--reps', '-r', type=int, default=10, help='run times, 10')
@click.option('--url', '-u', help='url, like 127.0.0.1:7777, ws://127.0.0.1:8000/echo', required=True)
@click.option('--msg_cmd', '-m', default=1, type=int, help='msg cmd, 1')
@click.option('--socket_type', '-t', default='socket', help='socket type, socket/websocket')
@click.option('--timeout', '-o', default=5, type=int, help='timeout, 5')
@click.option('--process_count', '-p', default=1, type=int, help='process count, 1')
def main(concurrent, reps, url, msg_cmd, socket_type, timeout, process_count):
    shock = Shock(concurrent, reps, url, msg_cmd, socket_type, timeout, process_count)
    shock.run()
    click.secho('done', fg='green')
    click.secho('Transactions:              %-10d hits' % shock.transactions)
    click.secho('Availability:              %-10.02f %%' % (shock.availability * 100))
    click.secho('Elapsed time:              %-10.02f secs' % shock.elapsed_time)
    click.secho('Response time:             %-10.02f secs' % shock.response_time)
    click.secho('Transaction rate:          %-10.02f trans/sec' % shock.transaction_rate)
    click.secho('Successful transactions:   %-10d hits' % shock.successful_transactions)
    click.secho('Failed transactions:       %-10d hits' % shock.failed_transactions)


if __name__ == '__main__':
    main()
