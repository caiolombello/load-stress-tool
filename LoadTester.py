import os
import requests
import threading
import time
import json
import random
import signal
import sys
from queue import Queue

class LoadTester:
    def __init__(self, method, url, auth_header, data, num_users, num_requests, wait_time, infinite=False, until_failure=False):
        self.method = method.upper()
        self.url = url
        self.auth_header = auth_header
        self.data = data
        self.num_users = num_users
        self.num_requests = num_requests
        self.wait_time = wait_time
        self.infinite = infinite
        self.until_failure = until_failure
        self.response_times = []
        self.success_count = 0
        self.total_count = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.start_time = time.time()

    def make_request(self):
        headers = {
            'Content-Type': 'application/json',
        }

        if self.auth_header:
            headers['authorization'] = self.auth_header

        while not self.stop_event.is_set():
            request_start_time = time.time()

            if self.method == 'POST':
                if self.data:
                    response = requests.post(self.url, headers=headers, data=json.dumps(self.data))
                else:
                    response = requests.post(self.url, headers=headers)
            elif self.method == 'GET':
                response = requests.get(self.url, headers=headers)

            request_end_time = time.time()

            elapsed_time = request_end_time - request_start_time
            current_time = time.time()
            elapsed_since_start = current_time - self.start_time
            with self.lock:
                self.response_times.append(elapsed_time)
                self.total_count += 1
                if response.status_code == 200:
                    self.success_count += 1
                print(f"[{self.method}] {self.url}")
                self.print_progress(response.status_code, elapsed_since_start)

            wait_time = self.wait_time
            time.sleep(wait_time)

            if not self.infinite and self.total_count >= self.num_requests:
                break

    def print_progress(self, status_code, elapsed_since_start):
        progress = self.total_count / (self.num_users * self.num_requests) * 100
        avg_response_time = sum(self.response_times) / len(self.response_times)
        print(f"[{status_code}] Progresso: {progress:.2f}%, Oscilação média: {avg_response_time:.2f} segundos, Tempo percorrido: {elapsed_since_start:.2f} segundos")

    def worker(self, request_queue):
        while not request_queue.empty() and not self.stop_event.is_set():
            request_queue.get()
            self.make_request()

    def run_test(self):
        def signal_handler(sig, frame):
            print("\nInterrompendo o teste...")
            self.stop_event.set()

        signal.signal(signal.SIGINT, signal_handler)

        threads = []
        request_queue = Queue()
        
        for _ in range(self.num_users * self.num_requests):
            request_queue.put(None)

        start_time = time.time()
        for _ in range(self.num_users):
            t = threading.Thread(target=self.worker, args=(request_queue,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        end_time = time.time()

        self.elapsed_time = end_time - start_time
        self.print_results()

    def print_results(self):
        if len(self.response_times) > 0:
            avg_response_time = sum(self.response_times) / len(self.response_times)
        else:
            avg_response_time = 0
        if self.total_count > 0:
            success_rate = self.success_count / self.total_count * 100
        else:
            success_rate = 0

        print(f"\nTempo total: {self.elapsed_time:.2f} segundos")
        print(f"Total de requisições: {self.total_count}")
        print(f"Taxa de sucesso: {success_rate:.2f}%")

if __name__ == "__main__":

    method = os.environ.get("METHOD") or "null"
    if method == "null":
        method = input("Digite o método (GET ou POST): ")

    url = os.environ.get("URL") or "null"
    if url == "null":
        url = input("Digite a URL: ")

    auth_header = os.environ.get("AUTH_HEADER") or "null"
    if auth_header == "null":
        auth_header = input("Digite o cabeçalho de autorização: ")
    elif auth_header == "none":
        auth_header = None

    data_str = os.environ.get("DATA") or "null"
    if data_str == "null":
        data_str = input("Digite os dados (JSON): ")
    elif data_str == "none":
        data_str = None
    data = json.loads(data_str) if data_str is not None and data_str.strip() != "" else None

    num_users = os.environ.get("NUM_USERS")
    if num_users is None:
        num_users = int(input("Digite o número de usuários simultâneos: "))
    else:
        num_users = int(num_users)

    num_requests = os.environ.get("NUM_REQUESTS")
    if num_requests is None:
        num_requests = int(input("Digite o número de requisições por usuário: "))
    else:
        num_requests = int(num_requests)

    wait_time = os.environ.get("WAIT_TIME")
    if wait_time is None:
        wait_time = float(input("Digite o tempo de espera entre requisições em segundos: "))
    else:
        wait_time = float(wait_time)

    infinite = os.environ.get("INFINITE") or "null"
    if infinite == "null":
        infinite = input("Executar requisições infinitamente? (s/n): ")
        infinite = infinite.lower() == "s"
    else:
        infinite = infinite.lower() == "true"

    until_failure = os.environ.get("UNTIL_FAILURE") or "null"
    if until_failure == "null":
        until_failure = input("Executar requisições até falha? (s/n): ")
        until_failure = until_failure.lower() == "s"
    else:
        until_failure = until_failure.lower() == "true"

    load_tester = LoadTester(method, url, auth_header, data, num_users, num_requests, wait_time, infinite, until_failure)
    load_tester.run_test()


