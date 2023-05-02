import os
import subprocess

def test_loadtester():
    url = "https://httpbin.org/get"
    method = "GET"
    num_users = "1"
    num_requests = "1"

    env = os.environ.copy()
    env["URL"] = url
    env["METHOD"] = method
    env["NUM_USERS"] = num_users
    env["NUM_REQUESTS"] = num_requests

    result = subprocess.run(["python", "LoadTester.py"], env=env, text=True, capture_output=True)

    assert "Média de resposta" in result.stdout, "Média de resposta não encontrada na saída"
    assert "Taxa de sucesso" in result.stdout, "Taxa de saída não encontrada na saída"

if __name__ == "__main__":
    test_loadtester()
    print("LoadTester teste concluído com sucesso.")
