# Metricbeat

* [Youtube Tutorial - Docker ELK Metricbeat 教學](https://youtu.be/ocqhi23ETnw)

官方介紹可參考 [Metricbeat-Overview](https://www.elastic.co/guide/en/beats/metricbeat/current/metricbeat-overview.html).

這篇主要介紹 Metricbeat, 用來收集系統, process, cpu, ram 這些相關系統日誌.

先收集到這些資訊, 再轉發到 Elasticsearch 或 Logstash.

這篇文章的教學是直接轉發到 Elasticsearch.

啟動

```cmd
docker-compose -f metricbeat-compose.yml up -d
```

重啟

```cmd
docker-compose -f metricbeat-compose.yml restart
```

## 步驟流程

啟動後, 打開 ELK 找到 Observability 點選裡面的 Metrics,

![alt tag](https://i.imgur.com/ajJEgdM.png)

接著你應該就會看到系統的相關資訊

![alt tag](https://i.imgur.com/cVrMnzu.png)

![alt tag](https://i.imgur.com/C1mkrFi.png)
