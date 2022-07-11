# ELK - Index Lifecycle Management (ILM)

* [Youtube Tutorial - Index Lifecycle Management(ILM)教學](https://youtu.be/cFmBuzUgAQ8)

之前介紹 [刪除 elasticsearch index 教學](https://github.com/twtrubiks/docker-elk-tutorial/tree/elk-7.6.0#%E5%88%AA%E9%99%A4-elasticsearch-index-%E6%95%99%E5%AD%B8) 時,

有大大提出更棒的 Lifecycle, 所以今天就來介紹他,

官網介紹 [Configure a lifecycle policy](https://www.elastic.co/guide/en/elasticsearch/reference/current/set-up-lifecycle-policy.html)

有四個階段,

`Hot` 可以寫入, 可以查詢

`Warm` 不能寫入, 可以查詢

`Cold` 不能寫入, 可以查詢(但較慢)

`Delete` 就是刪除的意思

## 如何執行指令

可以直接貼到你的 terminal,

也可以到 copy paste 到 Dev Tools (他會自動幫你把多餘的轉換掉)

![alt tag](https://i.imgur.com/FpjtVzY.png)

## 教學

新增 policy

```cmd
curl -u elastic:changeme -X PUT "localhost:9200/_ilm/policy/nginx_ilm_policy?pretty" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_age":"12s"
          }
        }
      },
      "delete": {
        "min_age": "10s",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'
```

12秒後 Rollover 執行,

再 10秒後 會轉到 delete 階段刪除.

位置在 Stack Management -> Index Lifecycle Policies

成功建立了 nginx_ilm_policy,

![alt tag](https://i.imgur.com/BbQhpQ1.png)

還有很多可以設定, 像是依照容量, 或是 docs 數量.

```json
{
    "actions": {
        "rollover": {
            "max_age":"15s",
            "max_size": "50gb",
            "max_docs": 100
        }
    }
}
```

有 Warm, Cold 階段範例,

```cmd
curl -u elastic:changeme -X PUT "localhost:9200/_ilm/policy/nginx_ilm_policy?pretty" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_age":"30s"
          }
        }
      },
      "warm": {
        "min_age": "5s",
        "actions": {}
      },
      "cold": {
        "min_age": "10s",
        "actions": {}
      },
      "delete": {
        "min_age": "15s",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'

```

新增 index template

```cmd
curl -u elastic:changeme -X PUT "localhost:9200/_index_template/nginx_ilm_template?pretty" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["nginx_logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "index.lifecycle.name": "nginx_ilm_policy",
      "index.lifecycle.rollover_alias": "nginx_logs"
    }
  }
}
'
```

位置在 Index Lifecycle Policies -> Index Templates

成功建立了 nginx_ilm_template

![alt tag](https://i.imgur.com/eEmgWRF.png)

建立初始索引 Index

```cmd
curl -u elastic:changeme -X PUT "localhost:9200/nginx_logs-1" -H 'Content-Type: application/json' -d'
{
  "aliases": {
    "nginx_logs": {
      "is_write_index":true
    }
  }
}
'
```

修改 poll_interval 時間 (方便測試先改成 10秒)

```cmd
curl -u elastic:changeme -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "indices.lifecycle.poll_interval":"10s"
  }
}
'
```

如果沒有設定, 預設就是 10 分鐘

```cmd
❯ curl -u elastic:changeme -X GET "localhost:9200/_cluster/settings"
{"persistent":{},"transient":{}}
```

還原預設 (預設就是 10 分鐘)

```cmd
curl -u elastic:changeme -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "indices.lifecycle.poll_interval":null
  }
}
'
```

發送資料測試

```cmd
curl -u elastic:changeme -X POST "localhost:9200/nginx_logs/_doc" -H 'Content-Type: application/json' -d'
{
  "@timestamp": "2022-11-22T23:10:00",
  "message": "GET /search HTTP/1.1 200 1070000"
}
'
```

觀看 index 的變化,

![alt tag](https://i.imgur.com/PVy4M81.png)

透過 [Explain lifecycle API](https://www.elastic.co/guide/en/elasticsearch/reference/current/ilm-explain-lifecycle.html) 查看目前狀況,

如果你自己在測試的時候發現無法到下一個階段(一直卡在 Warm 階段),

代表有某些地方設定不夠正確, 也就是你的 ELK 設定不夠完善,

如果夠 stability, 也有 cluster(多個node),

就會顯示綠燈, 而不是像我這樣顯示黃燈.

```cmd
curl -u elastic:changeme -X GET "localhost:9200/nginx_logs/_ilm/explain?pretty"
```

訊息為 Waiting for all shard copies to be active

```cmd
......
"step_info" : {
    "message" : "Waiting for all shard copies to be active",
    "shards_left_to_allocate" : -1,
    "all_shards_active" : false,
    "number_of_replicas" : 1
    }
......
```

可以手動將 index 修改成如下即可,

可參考 [Update index settings API](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-update-settings.html)

```cmd
curl -u elastic:changeme -X PUT "localhost:9200/nginx_logs/_settings" -H 'Content-Type: application/json' -d'
{
    "index" : {
        "number_of_replicas" : 0
    }
}
'
```

執行後, 會立刻執行 Rollover, 並且移動到下一個階段.

## filebeat 設定 ILM

修改 [filebeat.yml](https://github.com/twtrubiks/docker-elk-tutorial/blob/elk-7.6.0/docker-elk/filebeat/config/filebeat.yml),

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
setup.ilm.pattern: "{now/d}-000001"            # by daily
# setup.ilm.pattern: "{now/w{yyyy.ww}}-000001" # by weekly
setup.ilm.enabled: true
......
```

可參考 [Configure index lifecycle management](https://www.elastic.co/guide/en/beats/filebeat/7.17/ilm.html)

這邊要注意一下, 如果你有設定 enabled ilm,

`setup.template.name` 和 `setup.template.pattern` 會自動被忽略.

再到 Index Lifecycle Policies 中設定 policy.
