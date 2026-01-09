# KML-CLBS

![GitHub followers](https://img.shields.io/github/followers/kr1stoff)
![GitHub Created At](https://img.shields.io/github/created-at/kr1stoff/KML-CLBS)
![GitHub commit activity](https://img.shields.io/github/commit-activity/w/kr1stoff/KML-CLBS)
![GitHub Release](https://img.shields.io/github/v/release/kr1stoff/KML-CLBS)
![GitHub License](https://img.shields.io/github/license/kr1stoff/KML-CLBS)

CLBS(Centrel Laboratory Bioinformatics Servies)

## 配置

- 创建 clbs 目录

  ```bash
  # 上传,静态文件,下载
  mkdir -p /data/share/clbs/uploads
  mkdir -p /data/share/clbs/static
  mkdir -p /data/share/clbs/downloads
  # nginx
  mkdir -p /data/share/clbs/var/log/nginx
  mkdir -p /data/share/clbs/var/run
  ```

## 运行

- 运行项目
  查看端口占用

  ```bash
  # flask
  lsof -i:5000
  # nginx
  lsof -i:5001
  ```

  运行

  ```bash
  # flask
  cd /data/mengxf/GitHub/KML-CLBS
  # 生产
  poetry run waitress-serve --listen=0.0.0.0:5000 --call 'src.kml_clbs:create_app'
  # 测试
  poetry run flask --app src.kml_clbs run --debug --host 0.0.0.0 --port 5000

  # 启动 nginx
  # 运行前先测试
  # nginx -c /data/mengxf/GitHub/KML-CLBS/src/kml_clbs/config/nginx.conf -t
  # 开启
  nginx -c /data/mengxf/GitHub/KML-CLBS/src/kml_clbs/config/nginx.conf
  # 关闭 nginx 进程 (如果要重启)
  # nginx -c /data/mengxf/GitHub/KML-CLBS/src/kml_clbs/config/nginx.conf -s stop
  # 如果不能关闭就kill, 使用 lsof -i:5001 查看进程ID
  # kill -9 <进程ID>
  ```

  *注意*：
  （Claude）如果引发如下警告，可以忽略。首次启动默认访问 `/var/log/nginx/error.log`，后续的报错会写入到配置文件中的 `error_log` 路径

  ```text
  nginx: [alert] could not open error log file: open() "/var/log/nginx/error.log" failed (13: Permission denied)
  nginx: the configuration file /data/mengxf/GitHub/KML-CLBS/src/kml_clbs/nginx/conf.d/default.conf syntax is ok
  nginx: configuration file /data/mengxf/GitHub/KML-CLBS/src/kml_clbs/nginx/conf.d/default.conf test is successful
  ```
