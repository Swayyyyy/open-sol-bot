# 缓存预加载微服务

此微服务负责预加载和维护各种缓存数据，以提高主应用程序的性能。

## 项目结构

```
cache_preloader/
├── __init__.py           # 包初始化文件
├── main.py               # 主入口点
├── core/                 # 核心组件
│   ├── __init__.py       # 核心包初始化文件
│   ├── protocols.py      # 协议定义
│   └── base.py           # 基础类实现
├── caches/               # 具体缓存实现
│   ├── __init__.py       # 缓存包初始化文件
│   ├── blockhash.py      # 区块哈希缓存
│   ├── min_balance_rent.py # 最小租金余额缓存
│   └── raydium_pool.py   # Raydium 池缓存
└── services/             # 服务实现
    ├── __init__.py       # 服务包初始化文件
    └── auto_update_service.py # 自动更新服务
```

## 组件说明

### 核心组件 (core/)

- **protocols.py**: 定义缓存系统的协议接口
- **base.py**: 实现基础缓存类，提供通用功能

### 缓存实现 (caches/)

- **blockhash.py**: 区块哈希缓存实现
- **min_balance_rent.py**: 最小租金余额缓存实现
- **raydium_pool.py**: Raydium 池缓存实现

### 服务实现 (services/)

- **auto_update_service.py**: 自动更新缓存服务，协调和管理各种缓存的更新
