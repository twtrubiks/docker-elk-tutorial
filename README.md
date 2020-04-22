# docker-elk-tutorial 7.6.0

* [Youtube Tutorial - Linux 教學 - docker-elk-tutorial 7.6.0](https://youtu.be/iWFasUQ1tNQ)

這篇是 elk 基礎 2.0,

如果你還沒看過基礎篇, 請參考 [master分支](https://github.com/twtrubiks/docker-elk-tutorial/tree/master)

此 repo 是從 [docker-elk](https://github.com/deviantony/docker-elk) 修改過來的.

本篇會使用 odoo 的 log 來當範例, 請參考 [如何啟用 odoo 中的 Logging](https://github.com/twtrubiks/odoo-docker-tutorial#%E5%A6%82%E4%BD%95%E5%95%9F%E7%94%A8-odoo-%E4%B8%AD%E7%9A%84-logging)

## 教學

注意事項一.

在 [docker-elk/mydata/odoo.log](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/mydata/odoo.log) 中的 log 最後一行必須空一行(慣例),

![alt tag](https://i.imgur.com/FPK1ue5.png)

如果要放新的 `.log` 檔案進去, 請把舊的刪除

(否則會讀兩次, 因為在 [docker-elk/logstash/pipeline/logstash.conf]() 設定了 `start_position => beginning`).

注意事項二.

路徑底下的 [.env](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/.env) 很重要, 因為指令的 elk 的版本,

如果不懂這個 docker `.env` 功能, 請參考我之前寫的 [Docker 基本教學 - 在 docker compose 中善用 Environment variables](https://github.com/twtrubiks/docker-tutorial/tree/master/docker-env-tutorial)

直接只行以下的指令,

```cmd
docker-compose build
```

build 需要一點時間 (依照 `.env` 裡面指定的版本)

瀏覽 [0.0.0.0:5601](0.0.0.0:5601) 即可.

注意事項三.

原文 [How to disable paid features](https://github.com/deviantony/docker-elk#how-to-disable-paid-features)

將 [elasticsearch.yml](docker-elk/elasticsearch/config/elasticsearch.yml) 中的 `xpack.license.self_generated.type` 從 trial -> basic.

### grok 教學

參考檔案 [logstash/pipeline/logstash.conf](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/logstash/pipeline/logstash.conf)

如果有 log 可以使用以下兩種方法去測試,

* kibana 內建 Dev Tools (太舊的版本沒有內建)

![alt tag](https://i.imgur.com/lYbpg15.png)

使用方法很簡單,

input log

```log
2020-03-31 03:25:03,989 1 INFO twtrubiks werkzeug: 172.19.0.1 - - [31/Mar/2020 03:25:03] "GET /web/image?model=hr.employee&id=10&field=image_128&unique=03312020112413 HTTP/1.1" 200 - 5 0.004 0.012
```

pattern

```text
%{TIMESTAMP_ISO8601:logTimestamp} %{DATA:num} %{DATA:logType} %{DATA:Company} %{GREEDYDATA:detail} - %{NUMBER:query_count:int} %{NUMBER:query_time:float} %{NUMBER:remaining_time:float}
```

如果語法一切正確, 會正確的解析

![alt tag](https://i.imgur.com/mdJGqaA.png)

* 使用 grokdebug

[https://grokdebug.herokuapp.com/](https://grokdebug.herokuapp.com/)

如果語法一切正確, 會正確的解析

![alt tag](https://i.imgur.com/Ue8qDB1.png)

kibana 內可以依照自己定義的 field search

![alt tag](https://i.imgur.com/rWRzllV.png)

### kibana 設定時區

請到 Management -> Advanced Settings -> Timezone for date formatting 中設定時區,

![alt tag](https://i.imgur.com/k8UMh7c.png)

logTimestamp 為 server 時間,

local_time 為 本地時間 (logTimestamp + 8).

![alt tag](https://i.imgur.com/Lvu5y4r.png)
