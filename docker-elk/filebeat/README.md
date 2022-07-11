# Filebeat

* [Youtube Tutorial - Docker ELK Filebeat 教學](https://youtu.be/LS8RsFzbTFo)

* [Youtube Tutorial - Create daily indices 教學](https://youtu.be/A8EIa9FH8sY) - [文章快速連結](https://github.com/twtrubiks/docker-elk-tutorial/tree/elk-7.6.0/docker-elk/filebeat#create-daily-indices)

官方介紹可參考 [Filebeat-Overview](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-overview.html#filebeat-overview).

篇主要介紹 Filebeat, 用來收集日誌.

先收集到這些資訊, 再轉發到 Elasticsearch 或 Logstash.

這篇文章的教學是直接轉發到 Elasticsearch.

啟動

```cmd
docker-compose -f filebeat-compose.yml up -d
```

重啟

```cmd
docker-compose -f filebeat-compose.yml restart
```

這邊補充說明一下, 如果你的 docker 是使用 snap 安裝,

請修改你的
[filebeat-compose.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/filebeat/filebeat-compose.yml) 以及 [filebeat.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/filebeat/config/filebeat.yml),

因為他們的 docker 路徑是不一樣的,

[filebeat-compose.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/filebeat/filebeat-compose.yml),

```yml
services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:7.17.3
    ......
    volumes:
      - ./config/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro,Z
      - type: bind
        source: /var/lib/docker/containers
        target: /var/lib/docker/containers
        # snap install docker
        # source: /var/snap/docker/common/var-lib-docker/containers
        # target: /var/snap/docker/common/var-lib-docker/containers
    ......
```

[filebeat.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/filebeat/config/filebeat.yml),

```yml
......
- condition:
    contains:
      docker.container.name: odoo_docker_deploy_web_1
  config:
    - type: container
      paths:
        # - /var/lib/docker/containers/${data.docker.container.id}/*.log
        ## snap install docker
        - /var/snap/docker/common/var-lib-docker/containers/${data.docker.container.id}/*.log
      exclude_lines: ["^\\s+[\\-`('.|_]"]  # drop asciiart lines
......
```

## 步驟流程

啟動後, 打開 ELK 找到 Management 點選裡面的 Stack Management,

![alt tag](https://i.imgur.com/yDRIFdk.png)

點選 Kibana 裡的 Index Patterns

![alt tag](https://i.imgur.com/MIcw9DZ.png)

點選 Create index pattern

![alt tag](https://i.imgur.com/GQc2UE8.png)

如果你的 filebeat 有成功運行, 這裡會多出 filebeat 的 index

![alt tag](https://i.imgur.com/X07vCPp.png)

建立後到 Analytics 底下的 Dicscover 可看 log

![alt tag](https://i.imgur.com/redMyeU.png)

## 參數說明

如果你想要把當下 server 全部的 docker 容器的日誌都送到 ELK,

可以使用以下的設定

```conf
filebeat.autodiscover:
  providers:
    # The Docker autodiscover provider automatically retrieves logs from Docker
    # containers as they start and stop.
    - type: docker
      hints.enabled: true
```

你也可以定義你想送的 docker container,

分別可透過 docker.container.image 以及 docker.container.name 定義,

只轉發這兩個 container 的日誌.

```conf
filebeat.autodiscover:
  providers:
    # The Docker autodiscover provider automatically retrieves logs from Docker
    # containers as they start and stop.
    - type: docker
    #  hints.enabled: true
      templates:
        - condition:
            contains:
              docker.container.image: <docker image>
          config:
            - type: container
              paths:
                - /var/lib/docker/containers/${data.docker.container.id}/*.log
              exclude_lines: ["^\\s+[\\-`('.|_]"]  # drop asciiart lines
              multiline.pattern: '^[[:space:]]'
              multiline.negate: false
              multiline.match: after

        - condition:
            contains:
              docker.container.name: <docker container name>
          config:
            - type: container
              paths:
                - /var/lib/docker/containers/${data.docker.container.id}/*.log
      #          ## snap install docker
      #         - /var/snap/docker/common/var-lib-docker/containers/${data.docker.container.id}/*.log
              exclude_lines: ["^\\s+[\\-`('.|_]"]  # drop asciiart lines
              multiline.pattern: '^[[:space:]]'
              multiline.negate: false
              multiline.match: after

```

`multiline` 的參數說明, 我直接使用圖片和大家說明

未設定時(很亂, 因為都變成一行一行的)

![alt tag](https://i.imgur.com/uwJyy1U.png)

設定時(清楚多了, 訊息都被放在同一行)

![alt tag](https://i.imgur.com/OSdHVJc.png)

如果想參考更多設定說明,

* [Autodiscover](https://www.elastic.co/guide/en/beats/filebeat/current/configuration-autodiscover.html)

* [Hints based autodiscover](https://www.elastic.co/guide/en/beats/filebeat/current/configuration-autodiscover-hints.html#configuration-autodiscover-hints)

### filebeat.modules

在 filebeat 中有一個 `filebeat.modules` 可以設定,

這邊使用 nginx 當作例子,

[filebeat/config/filebeat.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/filebeat/config/filebeat.yml) 需加上

```conf
filebeat.modules:
 - module: nginx
   access:
     enabled: true
     var.paths: ["/usr/share/filebeat/nginx/access.log"]
   error:
     enabled: true
     var.paths: ["/usr/share/filebeat/nginx/error.log"]
```

[filebeat-compose.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/filebeat/filebeat-compose.yml) 也要加入你的 nginx log 路徑

```yml
services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:7.17.3
    ......
    volumes:
      ......
      - type: bind
        source: YOUR_NGINX_LOG/nginx_log/
        target: /usr/share/filebeat/nginx/
        read_only: true
......
```

nginx module 中會有一些直接就可以使用的 fields

![alt tag](https://i.imgur.com/OM0NPbA.png)

![alt tag](https://i.imgur.com/72QGR74.png)

更多詳細資料可參考 [filebeat-reference](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-reference-yml.html)

最後補充說明, 為什麼我的 nginx 要特別寫到檔案中, 不直接

將 nginx docker 的 stdout 送去 ELK 就好, 原因是因為

如果直接送, 會有亂碼 (terminal 的顏色造成的亂碼, 會影響分析:anguished:),

所以最後改成寫入檔案中:smile:

### Create daily indices

* [Youtube Tutorial - Create daily indices 教學](https://youtu.be/A8EIa9FH8sY)

這邊的設定是可以 daily 建立 index, weekly 建立 index,

可以依照自己的需求調整.

記住要加上 `setup.ilm.enabled: false`

```yml
output.elasticsearch:
  #hosts: ['http://elasticsearch:9200']
  hosts: ['YOUR_IP:9200']
  username: elastic
  password: changeme
  # create index by daily
  index: "filebeat1-%{[agent.version]}-%{+yyyy.MM.dd}"
  # create index by weekly
  # index: "filebeat1-%{[agent.version]}-%{+xxxx.ww}"

setup.template.name: "filebeat1"
setup.template.pattern: "filebeat1-*"
setup.ilm.enabled: false
```

![alt tag](https://i.imgur.com/5sS82EI.png)

官方文件可參考 [Configure the Elasticsearch output](https://www.elastic.co/guide/en/beats/filebeat/current/elasticsearch-output.html)
