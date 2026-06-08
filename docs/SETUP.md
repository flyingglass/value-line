# 开发环境配置规范

## 虚拟环境

本项目使用本地虚拟环境 `.venv`，**严禁**使用系统全局 Python 环境安装或运行项目依赖。

### 创建虚拟环境

```cmd
python -m venv .venv
```

### 安装依赖

所有 Python 包**必须**安装到 `.venv`，禁止使用全局 `pip`：

```cmd
.venv\Scripts\pip.exe install -r requirements.txt
```

### 运行脚本

必须使用虚拟环境中的 Python 解释器：

```cmd
.venv\Scripts\python.exe <script.py>
```

## 全局 Python 清理规则

**`requirements.txt` 中列出的所有包，不得存在于系统全局 Python 中。**

若发现全局 Python 中存在这些包，必须卸载：

```cmd
# 检查
python -m pip list | findstr /i "akshare pdfplumber requests pandas"

# 卸载（逐包）
python -m pip uninstall akshare pdfplumber requests pandas -y
```

> 注意：`pymysql` 是系统预装包，不要动。

## 依赖记录

项目依赖统一维护在 `requirements.txt`，新增依赖时必须同步更新该文件。

| 包名 | 最低版本 | 用途 |
|------|----------|------|
| akshare | >=1.18.0 | 金融数据获取 |
| pdfplumber | >=0.11.0 | PDF 解析 |
| requests | >=2.34.0 | HTTP 请求 |
| pandas | >=2.3.0 | 数据处理 |
