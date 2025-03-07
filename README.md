# 🤖 OpenSolBot

一个完全开源的 Solana 链上交易机器人，支持跟单交易和自动交易功能。 ⚡️

> 💡 这是一个开源的交易机器人项目，参考了 GMGN Bot 的实现。本项目完全开源，私钥由您自己保管，避免资产泄露风险。

## ⚠️ 免责声明

本项目仅作为个人学习和研究使用，不作为生产级别项目：

- 🎓 这是一个练习作品，主要用于学习和研究目的
- ⚠️ 不建议在生产环境中直接使用
- 📢 作者不对使用本项目造成的任何损失负责
- 💡 如果您决定使用本项目，请自行承担相关风险

## 🎯 演示

![Trading Bot Demo](https://github.com/user-attachments/assets/a4389538-b317-4858-a41d-b0f374d1a18f)

<details><summary>SWAP</summary>
<p>

![Image](https://github.com/user-attachments/assets/7005e10f-e599-414c-9520-b2e558f9e86b)

</p>
</details>

<details><summary>跟单</summary>
<p>

![Image](https://github.com/user-attachments/assets/653eb952-b8f9-4084-a0d3-42e719cc3043)

</p>
</details>

<details><summary>监控</summary>
<p>

![Image](https://github.com/user-attachments/assets/095f87f9-f95c-437a-b5ff-9a6a19e37fc6)

</p>
</details>

> 💬 交流群组: [https://t.me/chainbuff](https://t.me/chainbuff)
>
> ⚠️ **警告**：此机器人仅供测试体验使用
>
> - ❌ 请勿导入个人钱包
> - ❌ 请勿向钱包充值
> - 📢 测试数据可能随时被清除
> - 🔬 仅用于功能演示和测试

## ✨ 主要功能

- 💬 Telegram Bot
- 📊 跟单交易功能
- 🔍 监控功能
- 🎫 激活码系统
- 🔒 安全开源

## 💻 环境要求

- 🐍 Python 3.10+
- 📦 MySQL
- 🗄️ Redis
- 🐳 Docker (Recommended)

## 📥 快速开始

```bash
git clone https://github.com/mkdir700/open-sol-bot.git
cd open-sol-bot
```

## ⚙️ 配置说明

复制并编辑配置文件：

```bash
cp example.config.toml config.toml
```

### 必要配置

- `tg_bot.token`: Telegram Bot Token（[如何创建 Bot Token](https://core.telegram.org/bots#how-do-i-create-a-bot)）
- `rpc.endpoints`: RPC 节点列表，建议使用私有 RPC 节点，例如：Helius、Quicknode 等
- `api`: API 配置, 包括 [Helius](https://helius.dev) 和 [Shyft](https://shyft.to)，这些 API 有一定的免费额度，对于个人而言已经足够了。
  ```
  [api]
  helius_api_base_url = "https://api.helius.xyz/v0"
  helius_api_key = ""
  shyft_api_base_url = "https://api.shyft.to"
  shyft_api_key = ""
  ```
- `db`: 数据库连接配置，默认配置适用于本地开发环境。在 Docker 环境中会自动使用容器别名。
  ```
  [db]
  # 本地开发环境（从源码运行）
  mysql_url = "mysql+pymysql://root:root@127.0.0.1:3307/solana_trade_bot"
  redis_url = "redis://127.0.0.1:6380/0"
  ```

> 💡 为了获得更快的跟单速度，默认使用 `geyser` 模式，同时也支持 WebSocket 订阅方式

## 🚀 使用说明

Podman 请使用以下命令：

启动：

```
make up
```

停止服务：

```
make down
```

<details><summary>Docker 请使用以下命令:</summary>
<p>
启动：

```bash
docker compose up -d
```

停止服务：

```bash
docker compose down
```

</p>
</details>

更新：

```
git pull
podman/docker compose up -d --build
```

> 升级版本建议带上 `--build` 参数，这将重新构建容器

详细部署文档：[https://github.com/mkdir700/open-sol-bot/wiki/Deployment](https://github.com/mkdir700/open-sol-bot/wiki/Deployment)

## ⚠️ 注意事项

- 🔒 请确保配置文件中的私钥安全
- 💡 建议先使用小额资金测试
- 🌟 确保 RPC 节点的稳定性和可用性

## 🤝 如何贡献

我们非常欢迎您对本项目做出贡献！如果您想参与项目开发，请先阅读我们的[贡献指南](CONTRIBUTING.md)。

## 🙏 特别致谢

- Raydium 交易模块参考自 [AL-THE-BOT-FATHER/raydium_py](https://github.com/AL-THE-BOT-FATHER/raydium_py)
- Pump 交易模块参考自 [wisarmy/raytx](https://github.com/wisarmy/raytx/blob/main/src/pump.rs)

## 📄 许可证

[Apache 2.0](./LICENSE)
