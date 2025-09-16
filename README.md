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
  # 生产
  poetry run waitress-serve --listen=0.0.0.0:5000 --call 'src.kml_clbs:create_app'
  # 测试
  poetry run flask --app src.kml_clbs run --debug --host 0.0.0.0 --port 5000
  ```

  - `--host 0.0.0.0` 对外部访问可见

- 初始化数据库

  ```bash
  poetry run flask --app src.kml_clbs init-db
  ```

- 运行测试
  - 测试

    ```bash
    poetry run pytest
    ```

  - 测试覆盖率

    ```bash
    poetry run coverage run -m pytest
    ```

  - 测试覆盖率报告

    ```bash
    poetry run coverage html
    ```
  