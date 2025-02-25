# 🤝 如何贡献

我们非常欢迎并感谢您对本项目的贡献！以下是一些参与项目的方式：

## 提交 Issue

- 🐛 如果您发现了 bug，请提交 issue 并详细描述问题
- 💡 如果您有新功能建议，也欢迎提交 issue 讨论
- 📝 提交 issue 时请确保提供足够的信息，包括：
  - 问题描述
  - 复现步骤
  - 期望行为
  - 实际行为
  - 环境信息

## 提交 Pull Request

1. 🔀 Fork 本仓库
2. 🌿 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. ✍️ 提交您的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 📤 推送到分支 (`git push origin feature/AmazingFeature`)
5. 🔍 开启一个 Pull Request

## 开发环境要求

在开始开发之前，请确保您的环境满足以下要求：

### 必需组件

- 🐍 Python 3.10 或更高版本

  ```bash
  # 检查 Python 版本
  python --version
  ```

- 📦 PDM（Python 依赖管理工具）

  ```bash
  # 安装 PDM
  pip install pdm
  ```

- 🐳 容器运行时（选择一个）：
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/)（Windows/macOS）
  - [Podman Desktop](https://podman-desktop.io/)（推荐，全平台支持）
  ```bash
  # 检查 Docker 版本
  docker --version
  # 或检查 Podman 版本
  podman --version
  ```

### 推荐组件

- 📝 VSCode（推荐的代码编辑器）
- 🔧 Git（版本控制工具）
- 🐚 Windows 用户建议安装 [Git Bash](https://gitforwindows.org/) 或使用 WSL2

## 开发环境初始化

本项目使用 `make` 命令来管理开发环境和服务。根据您的操作系统，请选择对应的初始化方式：

### Windows 环境

Windows 用户可以选择以下两种方式之一：

#### 方式一：安装 Make（推荐）

1. 下载并安装 [Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm)
2. 将 Make 添加到系统环境变量
3. 然后可以使用与 Linux/macOS 相同的 `make` 命令

#### 方式二：直接使用等效命令

```powershell
# 初始化开发环境
pdm install -G dev -G local                 # 等效于 make dev-deps
docker compose up -d mysql redis            # 等效于 make infra-up

# 运行程序
docker compose up -d --build                # 等效于 make up
docker compose down -v                      # 等效于 make down

# 清理项目（可以使用 PowerShell 或 Git Bash）
Get-ChildItem -Recurse -Include "__pycache__","*.pyc","*.pyo","*.pyd",".pytest_cache",".coverage*","htmlcov","dist","build",".eggs" | Remove-Item -Recurse -Force
```

### Linux/macOS 环境

使用以下 `make` 命令：

```bash
# 完整初始化（包含安装依赖和启动基础设施）
make install

# 或者分步执行：
make dev-deps      # 仅安装开发依赖
make infra-up      # 仅启动基础设施（MySQL、Redis）

# 运行程序
make up            # 启动所有服务
make down          # 停止所有服务

# 其他命令
make build         # 重新构建 Docker 镜像
make clean         # 清理项目（删除缓存、构建文件等）
```

> 💡 注意：本项目默认使用 `podman` 作为容器运行时。如果您使用 `docker`，请修改 Makefile 中的 `DOCKER_EXEC` 变量或直接使用对应的 docker 命令。

## VSCode 开发环境配置

为了保持一致的开发体验，我们建议在 VSCode 中使用以下配置。将以下内容添加到您的 `.vscode/settings.json` 文件中：

```json
{
  "makefile.configureOnOpen": false,
  "python.testing.pytestArgs": ["tests"],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

这些设置将：

- 🔧 使用 ruff 作为默认的 Python 代码格式化工具
- ✨ 在保存时自动修复代码问题和组织导入
- 🧪 启用 pytest 作为测试框架
- 🛠️ 配置测试目录为 `tests`

请确保安装以下 VSCode 扩展：

- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 代码规范

- 遵循 PEP 8 Python 代码风格指南
- 添加必要的注释和文档
- 确保代码通过现有测试
- 为新功能添加测试用例

## Git Flow 工作流

![Git Flow](https://github.com/user-attachments/assets/d4a11407-1994-40c0-b3ec-33f3eb65fb8b)

本项目采用 Git Flow 工作流规范进行版本管理：

- 🌳 主分支
  - `main`: 生产环境分支，保持稳定
  - `develop`: 开发环境主分支
- 🌿 功能分支
  - `feature/*`: 新功能开发分支
  - `bugfix/*`: 问题修复分支
  - `hotfix/*`: 紧急修复分支
  - `release/*`: 版本发布分支

分支命名规范：

- `feature/功能名称`：如 `feature/wallet-integration`
- `bugfix/问题描述`：如 `bugfix/transaction-error`
- `hotfix/问题描述`：如 `hotfix/security-patch`
- `release/版本号`：如 `release/1.2.0`

## 其他贡献方式

- 📚 完善文档
- 🌍 改进翻译
- 🎨 优化用户界面
- 🔧 优化性能
- 📣 在社区中分享本项目

感谢所有贡献者为这个项目付出的努力！
