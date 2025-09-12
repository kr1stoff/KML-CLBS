# KML-CLBS

![GitHub followers](https://img.shields.io/github/followers/kr1stoff)
![GitHub Created At](https://img.shields.io/github/created-at/kr1stoff/KML-CLBS)
![GitHub commit activity](https://img.shields.io/github/commit-activity/w/kr1stoff/KML-CLBS)
![GitHub Release](https://img.shields.io/github/v/release/kr1stoff/KML-CLBS)
![GitHub License](https://img.shields.io/github/license/kr1stoff/KML-CLBS)

CLBS(Centrel Laboratory Bioinformatics Servies)

## 运行

- 运行项目

  ```bash
  poetry run flask --app src.kml_clbs run --debug --host 0.0.0.0 --port 5000
  ```

  - `--host 0.0.0.0` 对外部访问可见

- 初始化数据库

  ```bash
  poetry run flask --app src.kml_clbs init-db
  ```
