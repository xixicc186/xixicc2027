---
name: qiuzhao-feed
description: >-
  从 GitHub 仓库 xixicc186/xixicc2027 抓取最新的 2027 届秋招信息，并用喜茶风格前端页面
  在本地浏览器展示。当用户说"看看最新秋招"、"秋招信息"、"有什么新的校招/网申"、"哪些公司
  快截止了"、"看看互联网/央国企的秋招"、"打开秋招页面"、"qiuzhao"、"xixicc2027" 等任何
  查询秋招/校招/网申信息的场景时使用。支持按行业、关键词、截止日期过滤。数据每日更新在
  GitHub 上，本 skill 总是拉取远端最新数据，不要用本地 pipeline 的旧产出替代。
---

# qiuzhao-feed：秋招信息抓取与喜茶风格展示

## 数据源

GitHub 公开仓库 [xixicc186/xixicc2027](https://github.com/xixicc186/xixicc2027)，每日更新：

- `jobs.json` — 全部秋招条目（公司、行业、批次、岗位、地点、截止日、网申链接等）
- `site_template_heytea.html` — 喜茶风格前端模板，含 `/*__DATA__*/[]` 数据占位符
- `README.md` — 按行业分类的 Markdown 大表（互联网在前、央国企在后）
- 在线版：https://xixicc186.github.io/xixicc2027/

## 用法

一条命令完成"抓取 → 注入模板 → 生成 HTML → 打开浏览器"：

```bash
python3 ~/.claude/skills/qiuzhao-feed/scripts/fetch_render.py
```

按用户意图加过滤参数：

| 用户意图 | 参数 |
|---|---|
| 只看某行业（"看看互联网的"） | `--industry 互联网`（逗号分隔可多个） |
| 关键词（"有算法岗的"、"字节的"） | `--keyword 算法` |
| 快截止的（"哪些快截止了"） | `--days 7` |
| 只要数据不要开页面 | `--no-open` |
| 指定输出位置 | `--out /path/page.html` |

行业取值：互联网、游戏、半导体/硬件、新能源车企、传统车企、外企、快消/零售、
医药/生物、银行/金融、制造业、军工/研究所、高校/事业单位、央国企、其他。

## 脚本输出

stdout 会打印：总条数/筛选后条数、行业分布、7 天内截止清单、最新收录 10 条、
生成的页面路径。**把这些统计整理成中文简报回复给用户**，页面已自动在浏览器打开，
告知用户即可。

## 注意

- 脚本只用 Python 标准库，无需装依赖；数据从 raw.githubusercontent.com 拉取，
  需要网络。拉取失败时提示用户检查网络或稍后再试，不要改用本地文件兜底。
- 若用户想看原始表格而非页面，直接给 README 链接：
  https://github.com/xixicc186/xixicc2027/blob/main/README.md
- 模板占位符变更会导致脚本报错退出，此时去仓库确认 `site_template_heytea.html`
  的 `const JOBS = /*__DATA__*/[]` 行是否还在。
