# litemall-qa

[![ci](https://github.com/JINGTAO101/litemall-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/JINGTAO101/litemall-qa/actions/workflows/ci.yml)

针对开源商城 [litemall](https://github.com/linlinjava/litemall) 微信小程序后端（wx-api）的接口自动化。覆盖鉴权、购物车、订单提交与取消（当前约 19 条用例）。

litemall 在业务失败时 HTTP 仍经常是 200，结果看 JSON 的 `errno`（`0` 表示成功）。登录后的 JWT 放在请求头 `X-Litemall-Token`。用例除接口字段外，还会查 MySQL：`litemall_order`、`litemall_order_goods`、`litemall_goods_product`（库存）。

## 技术栈

| 用途 | 选型 |
| --- | --- |
| 接口自动化 | pytest、requests、allure-pytest |
| 数据库对账 | PyMySQL |
| 被测环境 | Docker Compose（MySQL 8.4 + wx-api） |
| 持续集成 | GitHub Actions：compose 就绪后跑全量 pytest |
| 负载 | Locust：登录后循环 `GET /wx/cart/index` |

本机配置在 `config/local.yaml`。

## 环境要求

- Docker Compose
- Python 3.13（与 CI 一致；3.11+ 一般可用）
- 查看 Allure 网页需要 JRE 与 Allure 命令行

端口：HTTP `8080`，MySQL `3308`。演示账号来自官方初始化脚本：`user123` / `user123`。

## 快速开始

仓库根目录（Windows PowerShell）：

```powershell
docker compose up -d --build
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -v
```

Linux / macOS 将解释器换成 `.venv/bin/python`。

Compose 会等 MySQL `healthcheck` 通过后再启动 Java。首次构建会从官方仓库 Maven 打包 wx-api，耗时可能超过 10 分钟。打包完成后仍需等到首页接口可用再跑测试：

```powershell
curl.exe --noproxy "*" http://127.0.0.1:8080/wx/index/index
```

响应 JSON 中 `"errno":0` 即表示被测已就绪。

## 持续集成

工作流：`.github/workflows/ci.yml`。

push 与 pull request 在 `ubuntu-latest` 上执行：`docker compose up -d --build` → 轮询 `GET /wx/index/index` 直至 `errno=0` → `pytest tests -v --alluredir=allure-results`。失败则 job 标红。无论成败都会 `compose down`，并把 `allure-results` 作为 Artifact 上传，可在 Actions 页面下载。

仓库尚未推送到 GitHub 时，上方徽章不会变绿。

## 报告

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v --alluredir=allure-results
allure generate --clean -o allure-report allure-results
allure open allure-report
```

失败用例可在 Allure 中查看请求与响应附件。`.venv/`、`allure-results/`、`allure-report/` 已列入 `.gitignore`。

## 负载测试

`locustfile.py`：每个虚拟用户 `on_start` 登录一次并写入 `X-Litemall-Token`，之后循环查询购物车。Locust 未写入 `requirements.txt`，需单独安装。

```powershell
.\.venv\Scripts\python.exe -m pip install locust
$env:NO_PROXY = "localhost,127.0.0.1"
.\.venv\Scripts\python.exe -m locust
```

浏览器打开 http://127.0.0.1:8089 ，Host 填 `http://127.0.0.1:8080`。请只压本机被测，并从少量用户起步。

## 目录结构

```
litemall-qa/
  tests/                      鉴权、购物车、订单
  common/                     HTTP 客户端、配置、数据库查询
  config/local.yaml           base_url 与库连接
  docker/                     官方 SQL 与 wx-api Dockerfile
  docker-compose.yml          MySQL + litemall（含 MySQL healthcheck）
  .github/workflows/ci.yml    GitHub Actions
  locustfile.py               负载脚本
```
