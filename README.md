# docker-elk-tutorial

docker-elk-tutorial📝

* [Youtube Tutorial PART 1 - ELK 簡介](https://youtu.be/T_sLKn3vXa4)
* [Youtube Tutorial PART 2 - docker ELK 環境建立](https://youtu.be/4JybtoFgC8g)
* [Youtube Tutorial PART 3 - 透過 python 送 log 到 ELK](https://youtu.be/EpEJGLzIK6A)
* [Youtube Tutorial PART 4 - logging for Django + ELK](https://youtu.be/_bkx0FfNRpQ)
* [Youtube Tutorial PART 5 - docker logging + ELK](https://youtu.be/gTqAjea4Ncg)

## 簡介

* [Youtube Tutorial PART 1 - ELK 簡介](https://youtu.be/T_sLKn3vXa4)

docker-elk :question: 這是什麼:question:  他可以吃嗎:confused:

重點在 **ELK** ，他是由三個東西所組成的。

[Elasticsearch](https://www.elastic.co/) ( E )

![img](https://i.imgur.com/qSbJRSv.png)

[Logstash](https://www.elastic.co/products/logstash) ( L )

![img](https://i.imgur.com/7sQUVqy.png)

[Kibana](https://www.elastic.co/products/kibana) ( K )

![img](https://i.imgur.com/eajQh99.png)

基本上，整個工作流程是這樣

![img](https://i.imgur.com/ZTDCjnD.png)

步驟一

Logstash 蒐集從 docker or 其他地方的 log 資訊，這個步驟主要是因為我們可以透過 [logstash.conf](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/docker-elk/logstash/pipeline/logstash.conf) 過濾

以及解析我們需要的資訊。

步驟二

Logstash 將處理完後的 log 資訊轉發到 Elasticsearch 進行 index。

步驟三

最後使用者可以透過 Kibana 分析以及視覺化所要的資料。

以上就是整個工作的流程，那他有什麼用呢 :confused:

像是分散式系統好了，之前介紹的 [docker swawm](https://github.com/twtrubiks/docker-swarm-tutorial)，每個容器的 log都進去一個一個看一定會累死，

所以這時候就可以統一把 log 送到 docker-elk 中，方便統一管理以及分析。

使用者的 log 非常重要，如果可以從 log 中分析出使用者愛好以及習慣，就可以推薦他類似的東西或

進行改善，當然，有一點很重要，就是這些 log 必須 **處理** 過，你可能會和我說可以用 AI（ AI 正夯 :expressionless: ）

但這不是這次的重點:relaxed:

由於這篇文章我會採用 Docker 建立 docker-elk，所以建議對 Docker 要有一定的認識，如果你不了解

Docker ，可參考我之前的 Docker 教學文章

* [Docker 基本教學 - 從無到有 Docker-Beginners-Guide](https://github.com/twtrubiks/docker-tutorial)

透過這篇文章，你將會學會

* [docker ELK 環境建立](https://github.com/twtrubiks/docker-elk-tutorial#docker-elk-%E7%92%B0%E5%A2%83%E5%BB%BA%E7%AB%8B)

* [透過 python 送 log 到 ELK](https://github.com/twtrubiks/docker-elk-tutorial#%E9%80%8F%E9%81%8E-python-%E9%80%81-log-%E5%88%B0-elk)

* [logging for Django + ELK](https://github.com/twtrubiks/docker-elk-tutorial#logging-for-django--elk) - Django 如何設定 logging 以及發送 logging 到 ELK 中

* [docker logging + ELK](https://github.com/twtrubiks/docker-elk-tutorial#docker-logging--elk) - 將 docker logs 發送到 docker ELK 中

## docker ELK 環境建立

* [Youtube Tutorial PART 2 - docker ELK 環境建立](https://youtu.be/4JybtoFgC8g)

我們直接使用 [docker-elk](https://github.com/deviantony/docker-elk) 這邊的 docker-compose.yml 即可，但因為我擔心版本會

更新（ 導致怪問題 ），所以我放一份到我自己的目錄下，建議閱讀一下 [docker-elk](https://github.com/deviantony/docker-elk)

中的 README.md，先到 [docker-elk](https://github.com/twtrubiks/docker-elk-tutorial/tree/master/docker-elk) 目錄底下

> cd  docker-elk

直接執行以下指令

> docker-compose up

第一次會比較慢，因為要 pull image 而且還要初始化 :sleeping:

這時候可以起來運動一下拉拉筋 :relaxed:

也可以用 `docker ps` 確認 docker-elk 都有正常運行

![img](https://i.imgur.com/OrprV0K.png)

[docker-compose.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/docker-elk/docker-compose.yml) 如果沒有特別修改，默認的 port 可參考下方

```conf
5000: Logstash TCP input
9200: Elasticsearch HTTP
9300: Elasticsearch TCP transport
5601: Kibana
```

以上是預設的，這邊我多加上一個 UDP 的 port

```conf
12201: Logstash UDP input
```

那要如何加，首先，在 docker-elk/[docker-compose.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/docker-elk/docker-compose.yml) 中加上 `12201:12201/udp`

```yml
  logstash:
    build:
      context: logstash/
    volumes:
      - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
    ports:
      - "5000:5000"
      - "12201:12201/udp"
    environment:
      LS_JAVA_OPTS: "-Xmx256m -Xms256m"
    networks:
      - elk
    depends_on:
      - elasticsearch
```

接著在 docker-elk/logstash/pipeline/[logstash.conf](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/docker-elk/logstash/pipeline/logstash.conf) 底下加上 udp

```conf
input {
    tcp {
        port => 5000
    }
    udp {
        port => 12201
    }
}

## Add your filters / logstash plugins configuration here

output {
    elasticsearch {
        hosts => "elasticsearch:9200"
    }
}

```

[logstash.conf](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/docker-elk/logstash/pipeline/logstash.conf) 可以設定的真的非常多，像是 filters ，大家可以自行去摸索，這邊先不介紹:smirk:

確認啟動成功後，我們可以先來看看 Elasticsearch，瀏覽
[http://localhost:9200/](http://localhost:9200/)

![img](https://i.imgur.com/4FcbOCm.png)

接著再來看看 Kibana（ 有時候你會發現無法瀏覽，這是因為還在初始化 ）

等待初始化完畢後，可以瀏覽 [http://localhost:5601/](http://localhost:5601/)，你應該會看到

![img](https://i.imgur.com/f9aYPd3.png)

我們需要先設定 index pattern，MAC 或 Linux 用戶直接使用以下指令

```cmd
curl -XPOST -D- "http://localhost:5601/api/saved_objects/index-pattern" \
    -H "Content-Type: application/json" \
    -H "kbn-version: 6.1.0" \
    -d "{'attributes':{'title':'logstash-*','timeFieldName':'@timestamp'}}"
```

如果你是 Windows 用戶，請用其他方法，雖然 Windows 也有 curl，但我裝上去執行指令，

他都會報錯說 josn格式錯誤，所以我直接改用 [Postman](https://www.getpostman.com/)

![img](https://i.imgur.com/lHh7thR.png)

如果一切順利，你應該會看到 response

![img](https://i.imgur.com/ideT84S.png)

接著重新整理 [http://localhost:5601/](http://localhost:5601/)，你應該會看到 index pattern 建立成功

![img](https://i.imgur.com/qB55XQp.png)

接著我們可以嘗試送送看 log , 如果你是 MAC 或 Linux 用戶，你可以使用以下指令

```cmd
nc localhost 5000 < README.md
```

上面這段指令其實只是將 README.md 往 logstash ( [http://localhost:5000/](http://localhost:5000/) ) 送資料，

可以透過 Kibana 觀看結果，會發現有一堆 [README.md](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/README.md) 的文字

![img](https://i.imgur.com/eSdsdcZ.png)

如果你是 Windows 用戶，請跳過這段 :laughing:

直接用 python 來測試吧:smirk:

## 透過 python 送 log 到 ELK

* [Youtube Tutorial PART 3 - 透過 python 送 log 到 ELK](https://youtu.be/EpEJGLzIK6A)

剛剛簡單的介紹 ELK，現在讓我們透過 python 送 log 到 ELK 吧 :satisfied:

建議大家可以先了解一下 python 中的 [logging](https://docs.python.org/3.6/howto/logging.html)，

也可以參考這個簡單的範例 [logging_tutorial.py](https://github.com/twtrubiks/python-notes/blob/master/logging_tutorial.py)。

要使用 python 發送 log 到 ELK，請先執行下列指令

[python-logstash](https://github.com/vklochan/python-logstash)

> pip install python-logstash

接著執行以下程式碼 python-logging/[demo_logging.py](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/python-logging/demo_logging.py)

```python
import logging
import logstash
import sys

host = 'localhost'

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)

# UDP
# test_logger.addHandler(logstash.LogstashHandler(host, 12201, version=1))

# TCP
test_logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))

test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
test_logger.warning('python-logstash: test logstash warning message.')

# add extra field to logstash message
extra = {
    'test_string': 'python version: ' + repr(sys.version_info),
    'test_boolean': True,
    'test_dict': {'a': 1, 'b': 'c'},
    'test_float': 1.23,
    'test_integer': 123,
    'test_list': [1, 2, '3'],
}
test_logger.info('python-logstash: test extra fields', extra=extra)
print('done,please see kibana')
```

接著可以到 Kibana 觀看

![img](https://i.imgur.com/mmPfRs6.png)

log 訊息的確是我們剛剛送出去的

![img](https://i.imgur.com/Rm4bVgQ.png)

如果你要測試 UDP 的部份，就把 TCP 註解，UDP 打開（ 取消註解 ），

這樣以後我們就可以將我們需要記錄的 log 資料通通都送到 ELK 中管理 :thumbsup:

## logging for Django + ELK

* [Youtube Tutorial PART 4 - logging for Django + ELK](https://youtu.be/_bkx0FfNRpQ)

剛剛介紹了如何透過 python 送 log 到 ELK 中，現在要教大家如何在 Django 中設定 logging :smirk:

如果不了解什麼是 Django，可參考我之前寫的 [Django 基本教學 - 從無到有 Django-Beginners-Guide 📝](https://github.com/twtrubiks/django-tutorial)

一樣請記得安裝 [python-logstash](https://github.com/vklochan/python-logstash) :blush:

> pip install python-logstash

我們就依照 [這篇](https://github.com/twtrubiks/django-tutorial) 的範例繼續介紹，

先將 django-tutorial/django-tutorial/[settings.py](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/django-tutorial/django-tutorial/settings.py) 加入下方程式碼

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logstash': {
            'level': 'WARNING',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'localhost',
            'port': 5000,  # Default value: 5000
            'version': 1,
            'message_type': 'django_logstash',  # 'type' field in logstash message. Default value: 'logstash'.
            'fqdn': False,  # Fully qualified domain name. Default value: false.
            'tags': ['django.request'],  # list of tags. Default: None.
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['logstash'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}
```

詳細的 django logging 可參考官網 [https://docs.djangoproject.com/en/2.0/topics/logging/](https://docs.djangoproject.com/en/2.0/topics/logging/)，

這邊要稍微提一下 [django.request](https://docs.djangoproject.com/en/2.0/topics/logging/#django-request)

```txt
django.request
Log messages related to the handling of requests.
5XX responses are raised as ERROR messages;
4XX responses are raised as WARNING messages.
```

接著到 django-tutorial/musics/[views.py](https://github.com/twtrubiks/django-tutorial/blob/master/musics/views.py)中修改程式碼

```python
from django.shortcuts import render

from musics.models import Music
from django.http import Http404

# Create your views here.
def hello_view(request):
    musics = Music.objects.all()
    # raise Exception('error !!!!')
    # raise Http404("sorry 404")
    return render(request, 'hello_django.html', {
        'data': "Hello Django ",
        'musics': musics,
})
```

以上註解的兩個地方，可以自行玩玩看，然後到 Kibana 中觀看，

如果不太理解，可參考影片的說明  [Youtube Tutorial PART 4 - logging for Django + ELK](https://youtu.be/_bkx0FfNRpQ)

`raise Exception('error !!!!')` 這行等於是 5XX responses，也就是 ERROR messages，

`raise Http404("sorry 404")` 這行等於是 ˋXX responses，也就是 WARNING messages。

## docker logging + ELK

* [Youtube Tutorial PART 5 - docker logging + ELK](https://youtu.be/gTqAjea4Ncg)

既然都講到這裡了，一定要來說一下如何將 docker 的 log 送到 ELK 中，

先來個 tcp 的簡單範例

```cmd
docker run --log-driver=syslog --log-opt syslog-address=tcp://0.0.0.0:5000 --log-opt syslog-facility=daemon alpine echo hello world tcp
```

![img](https://i.imgur.com/CNlAb98.png)

到 Kibana 觀看

![img](https://i.imgur.com/tWSFH1B.png)

再來個 udp 的簡單範例

```cmd
docker run --log-driver=gelf --log-opt gelf-address=udp://0.0.0.0:12201 alpine echo hello world udp
```

![img](https://i.imgur.com/DZpe15V.png)

這邊我覺得奇怪的是，如果用 gelf 送出去的 log 都會變成亂碼，

如果有人知道原因再請解答:sweat_smile:

![img](https://i.imgur.com/TobRFjw.png)

docker logging 詳細可參考 [https://docs.docker.com/engine/admin/logging/overview/](https://docs.docker.com/engine/admin/logging/overview/)

那如果我希望寫在 docker-compose 中呢？

請看 docker-logging/[docker-compose.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/docker-logging/docker-compose.yml)

```python
version: '3.3'
services:

    db:
      # container_name: 'postgres'
      image: postgres
      environment:
        POSTGRES_PASSWORD: password123
      ports:
        - "5432:5432"
        # (HOST:CONTAINER)
      volumes:
        - pgdata:/var/lib/postgresql/data/

    web:
      # build: ./api
      # command: python manage.py runserver 0.0.0.0:8000
      image: twtrubiks/my_django
      restart: always
      volumes:
        - api_data:/docker_api
        # (HOST:CONTAINER)
      ports:
        - "8000:8000"
        # (HOST:CONTAINER)
      depends_on:
        - db

      logging:
        driver: syslog
        options:
            syslog-address: tcp://0.0.0.0:5000
            tag: web-container-tcp

      # logging:
      #   driver: gelf
      #   options:
      #     gelf-address: udp://0.0.0.0:12201
      #     tag: web-container-udp

volumes:
    api_data:
    pgdata:
```

以上這個範例是從 [Docker 基本教學 - 從無到有 Docker-Beginners-Guide](https://github.com/twtrubiks/docker-tutorial)修改過來的，

一樣執行 `docker-compose up`，

![img](https://i.imgur.com/FjiW7K9.png)

接著到 Kibana 中可以看到 log 資訊

![img](https://i.imgur.com/Y0F8BSD.png)

## 後記：

這篇文章主要是帶大家對 ELK 有一些基本的觀念，因為 ELK 可以玩的東西真的非常的多，

坑很大，像是前面所說的 [logstash.conf](https://github.com/twtrubiks/docker-elk-tutorial/blob/master/docker-elk/logstash/pipeline/logstash.conf) 中可以設定的參數，像是 filters 之類的.......

又或是 Kibana 如何呈現精美的圖表，甚至將 docker-elk 佈署到 Swarm 中，都可以玩玩

看，所以大家有興趣可以再自行深入研究:smile:

我本來是想要透過 Django 結合 Haystack 做個全文檢索的範例，但因為 Haystack 對於

ElasticSearch 的版本只支援到 2.X  ( ElasticSearch 都出到 6.X 了 )，最後就沒有將這範例

寫出來了:sweat_smile:

[elasticsearch-py](https://github.com/elastic/elasticsearch-py) 這個 library 也可以看看，我用 6.x 版本測試，還是有一點問題，問題

如果解決再分享給各位:laughing:

## 執行環境

* Python 3.6.2

## Reference

* [docker-elk](https://github.com/deviantony/docker-elk)

* [python-logstash](https://github.com/vklochan/python-logstash)

* [Django](https://www.djangoproject.com/)

## License

MIT license