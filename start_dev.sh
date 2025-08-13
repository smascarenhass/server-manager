cd api
PORT=8000
if lsof -i :$PORT -t >/dev/null; then
    PID=$(lsof -i :$PORT -t)
    echo "Porta $PORT está em uso pelo processo $PID. Parando o processo..."
    kill -9 $PID
    sleep 1
fi
python main.py
