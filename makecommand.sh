pip install openai
pip install -U pyinstaller
pyinstaller --onefile chatgpt.py
sudo cp dist/chatgpt /usr/local/bin/