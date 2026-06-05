# 分发指南

## 打包成可下载应用

### macOS 打包

#### 1. 安装打包工具
```bash
pip install pyinstaller
```

#### 2. 运行打包脚本
```bash
cd /Users/mac/comment_collector
python build.py
```

#### 3. 输出文件
- 应用目录: `dist/评论采集工具/`
- 可执行文件: `dist/评论采集工具/评论采集工具`

#### 4. 创建 DMG 安装包（可选）
```bash
hdiutil create -volname "评论采集工具" -srcfolder "dist/评论采集工具" -ov -format UDZO "dist/评论采集工具.dmg"
```

### Windows 打包

#### 1. 在 Windows 环境执行
```bash
python build.py
```

#### 2. 输出文件
- 应用目录: `dist/CommentCollector/`
- 可执行文件: `dist/CommentCollector/CommentCollector.exe`

#### 3. 创建安装包（可选）
使用 NSIS 或 Inno Setup 创建 Windows 安装程序。

---

## 分发方式

### 方式一：直接分发压缩包

1. 将 `dist/` 目录下的应用文件夹压缩成 zip
2. 上传到网盘或文件托管服务
3. 用户下载解压后直接运行

### 方式二：GitHub Release

1. 在 GitHub 仓库创建 Release
2. 上传打包好的文件
3. 用户从 Release 页面下载

### 方式三：应用商店

#### macOS App Store
1. 注册 Apple Developer 账号
2. 使用 Xcode 打包签名
3. 提交审核

#### Windows Microsoft Store
1. 注册开发者账号
2. 打包成 MSIX 格式
3. 提交审核

---

## 自动化打包（GitHub Actions）

创建 `.github/workflows/build.yml`:

```yaml
name: Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build-mac:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: playwright install chromium
      - run: python build.py
      - uses: actions/upload-artifact@v3
        with:
          name: mac-app
          path: dist/

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: playwright install chromium
      - run: python build.py
      - uses: actions/upload-artifact@v3
        with:
          name: windows-app
          path: dist/
```

---

## 用户安装说明

### macOS 用户
1. 下载 `评论采集工具.dmg`
2. 双击打开 DMG
3. 将应用拖入 Applications 文件夹
4. 首次运行需要在"系统偏好设置 > 安全性与隐私"中允许运行

### Windows 用户
1. 下载 `CommentCollector.zip`
2. 解压到任意目录
3. 运行 `CommentCollector.exe`
4. 如果 Windows Defender 提示，选择"仍要运行"

---

## 注意事项

1. **代码签名**: 正式分发建议购买代码签名证书，避免安全警告
2. **Playwright 浏览器**: 打包时会包含 Chromium，文件较大（约 100-200MB）
3. **更新机制**: 可以集成 auto-updater 实现自动更新
4. **日志收集**: 建议添加崩溃日志上报功能
