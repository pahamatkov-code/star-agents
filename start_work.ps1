$path = "C:\Users\Matkovskiy Pavlo\ai_agent_project"
cd "$path"

# 1. Відкриваємо код
code .

# 2. Відкриваємо браузер
Start-Process "https://github.com"
Start-Process "http://localhost:8000"

# 3. Запуск терміналу (найпростіший варіант без помилок)
# Ми просто просимо термінал запустити PowerShell у папці проекту
wt -d "$path" powershell -noExit -Command ".\venv\Scripts\Activate.ps1"
