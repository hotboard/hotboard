# Changelog

## [0.0.2] - 2026-03-22

### Added

- 新增今日头条热榜平台

### Fixed

- 修复 Python 3.10 兼容性问题，要求 Python 3.11+
- 修复缺失的 feedparser 依赖

## [0.0.1] - 2026-03-22

### Added

- 多平台热榜数据获取，聚合国内外主流资讯、社区、视频等平台
- 统一 CLI 接口：`hotboard <platform>`
- `hotboard list` 命令列出所有平台
- JSON 和 Markdown 输出格式
- 自动发现平台，无需手动注册
