#!/usr/bin/env python3
"""
gen_resume_pdf.py — 将 baogong 简历 HTML 渲染为打印级 PDF（字体子集化，<500KB）

管线：Playwright Chromium（无头）渲染 → PyMuPDF 字体子集化 + deflate 压缩
为什么不用浏览器"另存为 PDF"：Chrome 会把完整 TNR 字体（~600KB）嵌入 PDF，
导致一页纯文本简历膨胀到 900KB+；本管线只嵌入实际用到的字符子集，正常 ~100KB。

依赖：
    pip install playwright pymupdf
    playwright install chromium

用法：
    python gen_resume_pdf.py <input.html> <output.pdf>

退出码：
    0 = 成功
    1 = 参数错误
    2 = 缺少依赖（playwright / pymupdf 未装）
    3 = 渲染或压缩失败
"""
import sys
from pathlib import Path

# Playwright 传 margin=0，由 CSS @page(8mm) + body padding(8mm 10mm) 控制内边距，
# 避免与 @page margin 重复导致双内边距。
MARGIN = {"top": "0", "bottom": "0", "left": "0", "right": "0"}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: gen_resume_pdf.py <input.html> <output.pdf>", file=sys.stderr)
        return 1

    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    raw = out.with_name(out.stem + ".raw.pdf")

    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 3

    # ---- 1. 依赖检查 ----
    try:
        from playwright.sync_api import sync_playwright
        import fitz  # PyMuPDF
    except ImportError as e:
        print(f"MISSING_PREREQ: pip install playwright pymupdf  ({e})", file=sys.stderr)
        return 2

    # ---- 2. 无头 Chromium 渲染 ----
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
            )
            page = browser.new_page()
            page.goto("file:///" + str(src).replace("\\", "/"), wait_until="networkidle")
            page.pdf(
                path=str(raw),
                format="A4",
                print_background=True,
                margin=MARGIN,
            )
            browser.close()
    except Exception as e:  # noqa: BLE001
        print(f"RENDER_FAILED: {e}", file=sys.stderr)
        return 3

    # ---- 3. 字体子集化 + 压缩 ----
    try:
        doc = fitz.open(raw)
        n_pages = doc.page_count
        doc.subset_fonts()
        doc.save(str(out), deflate=True, garbage=4, clean=True)
        doc.close()
    except Exception as e:  # noqa: BLE001
        print(f"COMPRESS_FAILED: {e}", file=sys.stderr)
        return 3
    finally:
        raw.unlink(missing_ok=True)

    size_kb = out.stat().st_size / 1024
    warn = "" if size_kb < 500 else "  ⚠️ >500KB 请检查"
    print(f"OK: {out.name}  {size_kb:.1f} KB  pages={n_pages}{warn}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
