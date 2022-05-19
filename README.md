# docker-elk-tutorial 7.6.0

* [Youtube Tutorial - Linux 教學 - docker-elk-tutorial 7.6.0](https://youtu.be/iWFasUQ1tNQ)

這篇是 elk 基礎 2.0,

如果你還沒看過基礎篇, 請參考 [master分支](https://github.com/twtrubiks/docker-elk-tutorial/tree/master)

此 repo 是從 [docker-elk](https://github.com/deviantony/docker-elk) 修改過來的.

本篇會使用 odoo 的 log 來當範例, 請參考 [如何啟用 odoo 中的 Logging](https://github.com/twtrubiks/odoo-docker-tutorial#%E5%A6%82%E4%BD%95%E5%95%9F%E7%94%A8-odoo-%E4%B8%AD%E7%9A%84-logging)

## 其他 extensions 教學

### Apm-Server

* [apm-server](https://github.com/twtrubiks/docker-elk-tutorial/tree/elk-7.6.0/docker-elk/apm-server) - [Youtube Tutorial - Docker ELK APM services 教學](https://youtu.be/j_iNhl1Cp_Y)

### Beat

官方介紹以及架構圖 [What are Beats?](https://www.elastic.co/guide/en/beats/libbeat/8.1/beats-reference.html)

Beat 通常可以發給 Elasticsearch 或 Logstash, 如果沒有要進一步的處理資料,

通常會直接轉發給 Elasticsearch, 除非要進一步處理資料, 才會轉發給 Logstash,

而且 Logstash 對 ram, cpu, io 這類消耗比較高.

Beat 家族有很多, 都屬於輕量級收集日誌的工具, 這邊只介紹以下幾個,

* [filebeat](https://github.com/twtrubiks/docker-elk-tutorial/tree/elk-7.6.0/docker-elk/filebeat) - Log files and journals - [(等待新增)Youtube Tutorial - Docker ELK Filebeat 教學]()

* [metricbeat](https://github.com/twtrubiks/docker-elk-tutorial/tree/elk-7.6.0/docker-elk/metricbeat) - Metrics - [(等待新增)Youtube Tutorial - Docker ELK Metricbeat 教學]()

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

## 刪除 elasticsearch index 教學

elasticsearch 上的 log 一定要記得定期刪除,

否則硬碟很快就會炸掉了,

提供兩種方法刪除, 分別是直接 call API, 或是使用 curator,

搭配自己喜歡的, 再加上 [crontab](https://github.com/twtrubiks/linux-note/tree/master/crontab-tutorual) 就可以自動刪除了.

### 使用 API

先使用 [cat indices API](https://www.elastic.co/guide/en/elasticsearch/reference/current/cat-indices.html),

取出你的 indices

```cmd
❯ curl -u elastic:changeme -GET http://YOUR_IP:9200/_cat/indices
green  open .apm-agent-configuration          mFn_ypTbQzimQ0Xnv6OV9A 1 0        0      0    226b    226b
green  open .tasks                            w_2xwED5QGCHCfML7KjhvA 1 0        5      0  28.1kb  28.1kb
green  open .geoip_databases                  h86_d2dDSVOREY32svJG9Q 1 0       41     41  38.8mb  38.8mb
```

`-u` 後面是你的帳號:密碼

之後在看你想要刪掉哪些,

再執行 ( 這邊刪除 `.apm-agent-configuration` )

```cmd
❯ curl -u elastic:changeme -XDELETE 'http://YOUR_IP:9200/.apm-agent-configuration*?pretty'
{
  "acknowledged" : true
}
```

這樣就成功刪除了.

### curator

另一種方法是使用 curator 這個 library,

安裝指令,

```cmd
pip install elasticsearch-curator
```

範例 code,

```python
import elasticsearch
import curator

client = elasticsearch.Elasticsearch(
    [
        "http://elastic:changeme@YOUR_IP:9200/",
    ],
    verify_certs=True,
)


ilo = curator.IndexList(client)
ilo.filter_by_regex(kind="prefix", value="myindex-")
# ilo.filter_by_age(source='name', direction='older', timestring='%Y.%m.%d', unit='days', unit_count=30)
delete_indices = curator.DeleteIndices(ilo)
delete_indices.do_action()
```

文件可參考

* [https://github.com/elastic/curator](https://github.com/elastic/curator)

* [https://www.elastic.co/guide/en/elasticsearch/client/curator/current/pip.html](https://www.elastic.co/guide/en/elasticsearch/client/curator/current/pip.html)

* [https://curator.readthedocs.io/en/latest/](https://curator.readthedocs.io/en/latest/)
