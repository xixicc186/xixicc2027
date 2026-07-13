#!/usr/bin/env python3
"""从 xixicc2027 GitHub 仓库拉取最新秋招数据，注入喜茶风格模板并生成本地 HTML。

用法：
  python3 fetch_render.py                       # 全量渲染并输出统计
  python3 fetch_render.py --industry 互联网      # 只看某行业（可多个，逗号分隔）
  python3 fetch_render.py --keyword 算法         # 公司/岗位关键词过滤
  python3 fetch_render.py --days 14             # 只看 N 天内截止的
  python3 fetch_render.py --out /path/page.html # 指定输出路径
  python3 fetch_render.py --no-open             # 只生成不打开浏览器

仅用标准库，无需安装依赖。"""
import argparse
import json
import sys
import tempfile
import urllib.request
import webbrowser
from datetime import date
from pathlib import Path

RAW = "https://raw.githubusercontent.com/xixicc186/xixicc2027/main"
PLACEHOLDER = "/*__DATA__*/[]"


def fetch(path):
    req = urllib.request.Request(f"{RAW}/{path}", headers={"User-Agent": "qiuzhao-feed"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--industry", help="行业过滤，逗号分隔，如: 互联网,游戏")
    ap.add_argument("--keyword", help="公司名/项目/岗位关键词过滤")
    ap.add_argument("--days", type=int, help="只保留 N 天内截止（含无截止日期的不保留）")
    ap.add_argument("--out", help="输出 HTML 路径，默认临时目录")
    ap.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    args = ap.parse_args()

    jobs = json.loads(fetch("jobs.json"))
    tpl = fetch("site_template_heytea.html")
    total = len(jobs)

    if args.industry:
        inds = {s.strip() for s in args.industry.split(",")}
        jobs = [j for j in jobs if (j.get("industry") or "其他") in inds]
    if args.keyword:
        kw = args.keyword
        jobs = [j for j in jobs if kw in json.dumps(
            [j["company"], j.get("program") or "", j["positions"]],
            ensure_ascii=False)]
    if args.days is not None:
        today = date.today()
        jobs = [j for j in jobs if j.get("deadline")
                and 0 <= (date.fromisoformat(j["deadline"]) - today).days <= args.days]

    if PLACEHOLDER not in tpl:
        sys.exit("模板中未找到数据占位符，仓库模板格式可能已变更")
    html = tpl.replace(PLACEHOLDER,
                       json.dumps(jobs, ensure_ascii=False, separators=(",", ":")))

    out = Path(args.out) if args.out else \
        Path(tempfile.mkdtemp(prefix="qiuzhao-")) / "qiuzhao.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    # 统计给 agent 汇报用
    by_ind = {}
    for j in jobs:
        by_ind[j.get("industry") or "其他"] = by_ind.get(j.get("industry") or "其他", 0) + 1
    urgent = sorted(
        (j for j in jobs if j.get("deadline")
         and 0 <= (date.fromisoformat(j["deadline"]) - date.today()).days <= 7),
        key=lambda j: j["deadline"])
    latest = sorted(jobs, key=lambda j: j["first_seen"], reverse=True)[:10]

    print(f"仓库共 {total} 条，筛选后 {len(jobs)} 条")
    print("行业分布:", "、".join(f"{k}×{v}" for k, v in
                             sorted(by_ind.items(), key=lambda x: -x[1])))
    if urgent:
        print(f"\n⏰ 7天内截止（{len(urgent)}条）:")
        for j in urgent[:15]:
            print(f"  {j['deadline']} {j['company']} {j.get('program') or ''}")
    print("\n🆕 最新收录:")
    for j in latest:
        print(f"  {j['first_seen']} {j['company']}"
              f"（{j.get('industry') or '其他'}·{j['batch']}）")
    print(f"\n页面: {out}")

    if not args.no_open:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
