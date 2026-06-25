"""HTML ↔ Markdown 변환 모듈"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def html_to_markdown(html: str) -> str:
    """
    Confluence HTML을 Markdown으로 변환

    Args:
        html: Confluence storage format 또는 view format HTML

    Returns:
        Markdown 문자열
    """
    try:
        import html2text
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = False
        converter.body_width = 0          # 자동 줄바꿈 비활성화
        converter.unicode_snob = True     # 유니코드 유지 (한글)
        converter.skip_internal_links = False
        converter.protect_links = True
        converter.wrap_links = False
        result = converter.handle(html)
        return result.strip()
    except ImportError:
        # html2text 없으면 간단한 태그 제거로 처리
        logger.warning("html2text not installed, falling back to basic conversion")
        return _basic_html_to_markdown(html)


def _basic_html_to_markdown(html: str) -> str:
    """html2text 없을 때 기본 변환"""
    md = html
    # 제목
    for i in range(1, 7):
        md = re.sub(rf'<h{i}[^>]*>(.*?)</h{i}>', lambda m, n=i: f"{'#'*n} {m.group(1)}", md, flags=re.DOTALL)
    # Bold
    md = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', md, flags=re.DOTALL)
    md = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', md, flags=re.DOTALL)
    # Italic
    md = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', md, flags=re.DOTALL)
    # 링크
    md = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', md, flags=re.DOTALL)
    # 이미지
    md = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/>', r'![\2](\1)', md)
    # 코드
    md = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', md, flags=re.DOTALL)
    md = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\n```\n\1\n```\n', md, flags=re.DOTALL)
    # 단락/줄바꿈
    md = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', md, flags=re.DOTALL)
    md = re.sub(r'<br\s*/?>', '\n', md)
    # 목록
    md = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', md, flags=re.DOTALL)
    md = re.sub(r'<[ou]l[^>]*>', '', md)
    md = re.sub(r'</[ou]l>', '\n', md)
    # 나머지 태그 제거
    md = re.sub(r'<[^>]+>', '', md)
    # HTML 엔티티 변환
    md = md.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    md = md.replace('&nbsp;', ' ').replace('&quot;', '"')
    # 연속 공백 정리
    md = re.sub(r'\n{3,}', '\n\n', md)
    return md.strip()


def markdown_to_html(markdown: str) -> str:
    """
    Markdown을 Confluence storage format HTML로 변환

    Args:
        markdown: Markdown 문자열

    Returns:
        Confluence storage format HTML
    """
    try:
        import markdown as md_lib
        html = md_lib.markdown(
            markdown,
            extensions=['tables', 'fenced_code', 'codehilite', 'nl2br']
        )
        return html
    except ImportError:
        logger.warning("markdown not installed, falling back to basic conversion")
        return _basic_markdown_to_html(markdown)


def _basic_markdown_to_html(markdown: str) -> str:
    """markdown 라이브러리 없을 때 기본 변환"""
    html = markdown
    # 제목
    for i in range(6, 0, -1):
        html = re.sub(rf'^{"#"*i}\s+(.*?)$', rf'<h{i}>\1</h{i}>', html, flags=re.MULTILINE)
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    # Italic
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    # 코드블록
    html = re.sub(r'```(?:\w+)?\n(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    # 인라인 코드
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    # 링크
    html = re.sub(r'\[([^\]]*)\]\(([^)]*)\)', r'<a href="\2">\1</a>', html)
    # 이미지
    html = re.sub(r'!\[([^\]]*)\]\(([^)]*)\)', r'<img src="\2" alt="\1"/>', html)
    # 목록
    html = re.sub(r'^[-*]\s+(.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # 단락
    lines = html.split('\n\n')
    html = ''.join(
        f'<p>{line.strip()}</p>' if not line.strip().startswith('<') else line
        for line in lines if line.strip()
    )
    return html


def extract_title_from_markdown(markdown: str) -> Optional[str]:
    """
    Markdown에서 첫 번째 H1 제목 추출

    Args:
        markdown: Markdown 문자열

    Returns:
        제목 문자열 또는 None
    """
    match = re.search(r'^#\s+(.+)$', markdown, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None
