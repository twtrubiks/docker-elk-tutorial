# Apm-Server

* [Youtube Tutorial - Docker ELK APM services 教學](https://youtu.be/j_iNhl1Cp_Y)

官方介紹以及架構圖可參考 [apm-components](https://www.elastic.co/guide/en/apm/guide/current/apm-components.html).

APM 全名是 Application Performance Monitoring,

簡單說, 就是監控你的 Application 的效能.

啟動

```cmd
docker-compose -f apm-server-compose.yml up -d
```

重啟

```cmd
docker-compose -f apm-server-compose.yml restart
```

## 建立 agent 連接到 APM Server

這邊使用 flask, 請安裝以下套件

```cmd
pip3 install flask
pip3 install "elastic-apm[flask]"
```

範例 code 如下

```python
import elasticapm
from elasticapm.contrib.flask import ElasticAPM

from flask import Flask

app = Flask(__name__)

app.config['ELASTIC_APM'] = {
    # Set required service name. Allowed characters:
    # a-z, A-Z, 0-9, -, _, and space
    'APP_NAME': 'flask-apm-client',
    # Use if APM Server requires a token
    'SECRET_TOKEN': '',
    'SERVICE_NAME': 'PYTHON_FLASK_TEST_APP',
    'SERVER_URL': 'http://YOUR_IP:8200',
    'DEBUG': True,
}

apm = ElasticAPM(app)

@app.route('/test')
def test():
    return "test"

@app.route('/slow')
def slow():
    import time
    time.sleep(5)
    return "slow"

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
```

執行指令

```cmd
export FLASK_APP=client.py
flask run
```

官方 APM Pyhton 文件可參考 [Flask support](https://www.elastic.co/guide/en/apm/agent/python/current/flask-support.html)

## 步驟流程

先啟動你的 ELK, 然後再啟動 APM server,

之後把 Flask Agent Client 執行起來.

### 設定 APM server

打開 ELK 找到 Observability 點選裡面的 APM,

![alt tag](https://i.imgur.com/aAbbre1.png)

點選 Add the APM integration

![alt tag](https://i.imgur.com/xsO0oZm.png)

選擇 Elastic APM in Fleet 這個 tab,

底下點選一下 Check APM Server status,

正常的化會跳出 You have correctly setup APM Server

![alt tag](https://i.imgur.com/VTpgxIt.png)

至於下面的 Agent status 我覺得不需要理他,

我自己測試有成功收到資料, 但這邊就是會說沒收到:smirk:

你只要確定你的 Flask Agent Client 有成功執行起來,

然後進去 flask 隨便瀏覽幾個 url.

![alt tag](https://i.imgur.com/rqofuJv.png)

最後點選 Load Kibana objects 和 Launch APM 即可.

![alt tag](https://i.imgur.com/8ojddw6.png)

成功建立了

![alt tag](https://i.imgur.com/598SC6P.png)

這邊有每個 request 的細節

![alt tag](https://i.imgur.com/VMo7ZzK.png)
