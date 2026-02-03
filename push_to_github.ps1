# GitHub推送脚本
# 使用方法：修改下方的$commitMessage变量，然后运行此脚本

# 设置推送注释
$commitMessage = "更新项目"

# 执行Git操作
Write-Host "开始推送代码到GitHub..."
Write-Host "推送注释: $commitMessage"
Write-Host ""

# 添加所有更改
Write-Host "1. 添加所有更改..."
& git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: git add 失败"
    exit 1
}
Write-Host "✓ git add 成功"
Write-Host ""

# 提交更改
Write-Host "2. 提交更改..."
$commitArgs = @("commit", "-m", $commitMessage)
& git @commitArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: git commit 失败"
    exit 1
}
Write-Host "✓ git commit 成功"
Write-Host ""

# 推送更改
Write-Host "3. 推送更改到GitHub..."
& git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "尝试设置上游分支..."
    & git push --set-upstream origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: git push 失败"
        exit 1
    }
}
Write-Host "✓ git push 成功"
Write-Host ""

# 完成
Write-Host "✅ 代码推送完成！"
Write-Host "推送注释: $commitMessage"
Write-Host ""
Write-Host "按任意键退出..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
$host.UI.RawUI.FlushInputBuffer()