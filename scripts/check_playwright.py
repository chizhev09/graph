import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("80.64.17.11", username="root", password="u@7aexn?YVS-34", timeout=60, allow_agent=False, look_for_keys=False)
for cmd in [
    "docker exec graph-backend-1 pip show playwright 2>&1",
    "docker exec graph-backend-1 test -d /home/graph/.cache/ms-playwright && echo BROWSER_CACHE_YES || echo BROWSER_CACHE_NO",
    "cd /opt/graph && docker compose ps -a",
]:
    print("===", cmd)
    _, o, _ = c.exec_command(cmd, timeout=30)
    print(o.read().decode())
c.close()
