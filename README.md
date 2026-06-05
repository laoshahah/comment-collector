# 评论采集工具

跨平台评论采集与客户信息提取工具，支持抖音、小红书、快手等平台。

## 功能特性

- 🔍 关键词搜索视频/帖子
- 💬 自动采集评论数据
- 📱 智能提取手机号、微信号、QQ号
- 🎯 自动判断客户意向度（高/中/低）
- 📊 数据筛选与导出 Excel
- 💾 本地数据存储，隐私安全

## 安装使用

### 方式一：直接运行（需要 Python 环境）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 Playwright 浏览器
playwright install chromium

# 3. 启动程序
python main.py
```

### 方式二：打包成可执行文件

```bash
# 安装打包工具
pip install pyinstaller

# 运行打包脚本
python build.py
```

打包完成后，可执行文件在 `dist/` 目录中。

## 使用说明

1. 启动程序后，在搜索面板输入关键词
2. 选择要爬取的平台（抖音/小红书/快手）
3. 点击"开始搜索"
4. 等待爬取完成，查看结果
5. 可按平台、意向度筛选数据
6. 点击"导出 Excel"保存数据

## 项目结构

```
comment_collector/
├── main.py              # 主入口
├── config.py            # 配置文件
├── build.py             # 打包脚本
├── requirements.txt     # 依赖列表
├── gui/                 # 界面模块
├── crawlers/            # 爬虫模块
├── parsers/             # 解析模块
├── storage/             # 存储模块
└── utils/               # 工具模块
```

## 技术栈

- Python 3.9+
- PyQt6 (GUI)
- Playwright (浏览器自动化)
- Pandas (数据处理)
- SQLite (本地存储)

## 注意事项

- 首次使用需要登录各平台账号
- 请合理设置爬取延时，避免被封号
- 仅用于公开数据采集，请遵守平台规则

## 许可证

MIT License
