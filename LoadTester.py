import os
import requests
import threading
import time
import json
from queue import Queue

class LoadTester:
    def __init__(self, url, auth_header, data, num_users, num_requests):
        self.url = url
        self.auth_header = auth_header
        self.data = data
        self.num_users = num_users
        self.num_requests = num_requests
        self.response_times = []
        self.success_count = 0
        self.total_count = 0
        self.lock = threading.Lock()

    def make_request(self):
        headers = {
            'Content-Type': 'application/json',
            'authorization': self.auth_header
        }

        start_time = time.time()
        response = requests.post(self.url, headers=headers, data=json.dumps(self.data))
        end_time = time.time()

        elapsed_time = end_time - start_time
        with self.lock:
            self.response_times.append(elapsed_time)
            self.total_count += 1
            if response.status_code == 200:
                self.success_count += 1
            self.print_progress(response.status_code)

    def print_progress(self, status_code):
        progress = self.total_count / (self.num_users * self.num_requests) * 100
        avg_response_time = sum(self.response_times) / len(self.response_times)
        print(f"[{status_code}] Progresso: {progress:.2f}%, Oscilação média: {avg_response_time:.2f} segundos")

    def worker(self, request_queue):
        while not request_queue.empty():
            request_queue.get()
            self.make_request()

    def run_test(self):
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
        success_rate = self.success_count / self.total_count * 100

        print(f"\nTempo total: {self.elapsed_time:.2f} segundos")
        print(f"Média de resposta: {avg_response_time:.2f} segundos")
        print(f"Total de requisições: {self.total_count}")
        print(f"Taxa de sucesso: {success_rate:.2f}%")

if __name__ == "__main__":
    url = os.environ.get("URL") or input("Digite a URL: ")
    auth_header = os.environ.get("AUTH_HEADER") or input("Digite o cabeçalho de autorização: ")
    data_str = os.environ.get("DATA") or input("Digite os dados (JSON): ")
    data = json.loads(data_str)
    num_users = int(os.environ.get("NUM_USERS") or input("Digite o número de usuários simultâneos: "))
    num_requests = int(os.environ.get("NUM_REQUESTS") or input("Digite o número de requisições por usuário: "))

    load_tester = LoadTester(url, auth_header, data, num_users, num_requests)
    load_tester.run_test()

