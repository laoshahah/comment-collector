# 快速开始指南

## 一、开发环境准备

### 1. 安装 Python 依赖
```bash
cd /Users/mac/comment_collector
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 安装 Playwright 浏览器
```bash
playwright install chromium
```

### 3. 生成应用图标（可选）
```bash
# 需要先安装 Pillow
pip install Pillow

# 生成图标
cd assets
python generate_icon.py
cd ..
```

---

## 二、运行应用

### 开发模式运行
```bash
python main.py
```

---

## 三、打包成可下载应用

### macOS 打包

```bash
# 1. 运行打包脚本
python build.py

# 2. 输出位置
# dist/评论采集工具/评论采集工具

# 3. 创建 DMG 安装包（可选）
python build.py --dmg
# 输出: dist/评论采集工具.dmg
```

### Windows 打包

```bash
# 在 Windows 环境执行
python build.py

# 输出位置
# dist/CommentCollector/CommentCollector.exe
```

---

## 四、分发应用

### 方式一：GitHub Release（推荐）

1. **创建 GitHub 仓库**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/comment-collector.git
git push -u origin main
```

2. **创建版本标签**
```bash
git tag v1.0.0
git push origin v1.0.0
```

3. **自动打包发布**
- GitHub Actions 会自动触发打包
- 打包完成后自动创建 Release
- 用户从 Release 页面下载

### 方式二：手动分发

1. 打包应用
```bash
python build.py
```

2. 压缩应用目录
```bash
# macOS
cd dist && zip -r 评论采集工具-mac.zip 评论采集工具/

# Windows
cd dist && zip -r CommentCollector-windows.zip CommentCollector/
```

3. 上传到网盘或文件托管服务

---

## 五、用户安装说明

### macOS 用户
1. 下载 `评论采集工具.dmg` 或 `评论采集工具-mac.zip`
2. 如果是 DMG：双击打开，拖入 Applications 文件夹
3. 如果是 ZIP：解压后双击运行
4. 首次运行可能需要：右键 > 打开（绕过安全提示）

### Windows 用户
1. 下载 `CommentCollector-windows.zip`
2. 解压到任意目录
3. 双击 `CommentCollector.exe` 运行
4. 如果 Windows Defender 提示：更多信息 > 仍要运行

---

## 六、自动更新配置

### 1. 修改更新地址
编辑 `updater/updater.py`，修改以下内容：
```python
GITHUB_OWNER = "your-username"  # 你的 GitHub 用户名
GITHUB_REPO = "comment-collector"  # 你的仓库名
```

### 2. 用户检查更新
- 菜单栏 > 帮助 > 检查更新
- 应用会自动检查 GitHub Release

### 3. 发布更新
1. 修改版本号
2. 推送代码
3. 创建新 Tag：`git tag v1.1.0 && git push origin v1.1.0`
4. GitHub Actions 自动打包发布
5. 用户端会检测到新版本

---

## 七、常见问题

### Q: macOS 提示"无法打开，因为无法验证开发者"
**解决方法**：
1. 系统偏好设置 > 安全性与隐私
2. 点击"仍要打开"
3. 或者右键 > 打开

### Q: Windows Defender 阻止运行
**解决方法**：
1. 点击"更多信息"
2. 点击"仍要运行"
3. 或将应用添加到白名单

### Q: 打包后应用很大（100MB+）
**原因**：包含了 Chromium 浏览器
**解决方法**：这是正常的，Playwright 需要浏览器才能运行

### Q: 如何减小应用体积？
```bash
# 使用 UPX 压缩
pip install upx
pyinstaller --upx-dir=/path/to/upx ...
```

---

## 八、项目结构

```
comment_collector/
├── main.py              # 主入口
├── config.py            # 配置文件
├── build.py             # 打包脚本
├── requirements.txt     # 依赖列表
├── setup.py             # pip 安装配置
├── README.md            # 项目说明
├── QUICKSTART.md        # 快速开始（本文件）
├── DISTRIBUTION.md      # 分发指南
├── assets/              # 资源文件
│   ├── icon.svg         # 图标源文件
│   ├── icon.icns        # macOS 图标
│   ├── icon.ico         # Windows 图标
│   └── generate_icon.py # 图标生成脚本
├── gui/                 # 界面模块
├── crawlers/            # 爬虫模块
├── parsers/             # 解析模块
├── storage/             # 存储模块
├── updater/             # 自动更新模块
└── utils/               # 工具模块
```
