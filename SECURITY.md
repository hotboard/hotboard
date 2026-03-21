# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

如果您发现了安全漏洞，请通过以下方式报告：

1. **不要**在公开 issue 中报告安全漏洞
2. 发送邮件至项目维护者（请在 GitHub profile 中查找联系方式）
3. 或通过 GitHub Security Advisory 私密报告

### 报告内容应包括：

- 漏洞描述
- 复现步骤
- 影响范围
- 可能的修复方案（如果有）

### 响应时间：

- 我们会在 48 小时内确认收到报告
- 在 7 天内提供初步评估
- 根据严重程度，在 30 天内发布修复版本

## Security Best Practices

使用本项目时，请注意：

1. **Rate Limiting**: 合理控制请求频率，避免对目标平台造成压力
2. **遵守 ToS**: 确保使用符合各平台的服务条款
3. **数据隐私**: 不要在公开场合分享包含敏感信息的输出
4. **依赖更新**: 定期更新依赖包以获取安全补丁
5. **环境隔离**: 建议在虚拟环境中运行

## Known Limitations

- 本项目依赖公开 API 和网页抓取，可能因目标平台变更而失效
- 部分平台可能有反爬虫机制，请合理使用
- 不保证数据的实时性和完整性
