# 贡献指南

感谢您对 Hotboard 项目的关注！

## 如何提交 Issue

- 使用清晰的标题描述问题
- 提供详细的复现步骤
- 说明预期行为和实际行为
- 提供环境信息（Python 版本、操作系统等）

## 如何提交 Pull Request

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 代码规范

- 使用 Python 3.12+
- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写清晰的文档字符串
- 确保所有测试通过

## 添加新平台

1. 在 `packages/hotboard/` 目录下创建新的平台模块
2. 遵循 `DEVELOPMENT.md` 中的开发规范
3. 编写测试用例
4. 更新文档

## 测试要求

- 所有新功能必须包含测试
- 确保现有测试通过
- 运行 `pytest tests/` 进行完整测试

## 开发环境

```bash
# 安装开发依赖
bash tests/install_dev.sh

# 运行测试
pytest tests/
```
