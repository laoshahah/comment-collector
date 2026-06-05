#!/bin/bash
# 一键推送到 GitHub 脚本

echo "=========================================="
echo "  评论采集工具 - GitHub 推送脚本"
echo "=========================================="
echo ""

# 检查是否已配置 Git 用户信息
if [ -z "$(git config --global user.name)" ] || [ -z "$(git config --global user.email)" ]; then
    echo "请先配置 Git 用户信息："
    echo ""
    read -p "请输入你的名字: " GIT_NAME
    read -p "请输入你的邮箱: " GIT_EMAIL

    git config --global user.name "$GIT_NAME"
    git config --global user.email "$GIT_EMAIL"
    echo "✓ Git 用户信息已配置"
fi

echo ""
echo "请在 GitHub 创建仓库："
echo "1. 打开 https://github.com/new"
echo "2. Repository name: comment-collector"
echo "3. 选择 Public"
echo "4. 不要勾选任何选项"
echo "5. 点击 Create repository"
echo ""

read -p "请输入你的 GitHub 用户名: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "错误：用户名不能为空"
    exit 1
fi

echo ""
echo "正在配置远程仓库..."

# 添加远程仓库
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/${GITHUB_USER}/comment-collector.git"

echo "✓ 远程仓库已配置"
echo ""

# 推送代码
echo "正在推送代码..."
echo "（如果提示输入密码，请输入 GitHub Personal Access Token）"
echo ""
echo "获取 Token: https://github.com/settings/tokens"
echo "权限勾选: repo (全部)"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 代码推送成功！"
    echo ""

    # 创建版本标签
    echo "正在创建版本标签..."
    git tag v1.0.0
    git push origin v1.0.0

    if [ $? -eq 0 ]; then
        echo ""
        echo "=========================================="
        echo "  ✓ 全部完成！"
        echo "=========================================="
        echo ""
        echo "GitHub Actions 将自动打包应用"
        echo "查看进度: https://github.com/${GITHUB_USER}/comment-collector/actions"
        echo "下载应用: https://github.com/${GITHUB_USER}/comment-collector/releases"
        echo ""
    fi
else
    echo ""
    echo "推送失败，请检查："
    echo "1. GitHub 用户名是否正确"
    echo "2. 仓库是否已创建"
    echo "3. 网络连接是否正常"
fi
