"""
知乎爬虫 - 简化版
"""
import re
from typing import List
from crawlers.base_crawler import BaseCrawler, CommentData
from utils.logger import logger
from utils.helpers import random_delay, clean_text, format_time


class ZhihuCrawler(BaseCrawler):
    """知乎爬虫"""

    def __init__(self):
        super().__init__()
        self.platform_name = "知乎"

    async def search(self, keyword: str, max_pages: int = 5) -> List[dict]:
        """搜索知乎"""
        results = []
        try:
            search_url = f"https://www.zhihu.com/search?type=content&q={keyword}"
            await self.safe_goto(search_url)
            await random_delay(5, 8)

            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await random_delay(3, 5)

            selectors = [
                '.SearchResult-Card',
                '.List-item',
                'div[class*="Card"]',
                'div[class*="item"]',
            ]

            items = []
            for selector in selectors:
                try:
                    items = await self.page.query_selector_all(selector)
                    if items:
                        logger.info(f"知乎: 使用选择器 {selector} 找到 {len(items)} 个结果")
                        break
                except:
                    continue

            if not items:
                content = await self.page.content()
                logger.warning(f"知乎: 未找到内容列表，页面长度: {len(content)}")
                return results

            for item in items[:20]:
                try:
                    title = ""
                    for title_sel in ['h2', 'a', 'span', 'div[class*="title"]']:
                        try:
                            el = await item.query_selector(title_sel)
                            if el:
                                text = await el.inner_text()
                                if text and len(text) > 5:
                                    title = text[:100]
                                    break
                        except:
                            continue

                    url = ""
                    try:
                        link_el = await item.query_selector('a[href*="/question/"], a[href*="/answer/"], a[href*="/article/"]')
                        if link_el:
                            url = await link_el.get_attribute("href")
                            if url and not url.startswith("http"):
                                url = "https://www.zhihu.com" + url
                    except:
                        pass

                    author = ""
                    for author_sel in ['.AuthorInfo-name', '[class*="name"]', 'a']:
                        try:
                            el = await item.query_selector(author_sel)
                            if el:
                                text = await el.inner_text()
                                if text and len(text) < 20:
                                    author = text
                                    break
                        except:
                            continue

                    if title:
                        results.append({
                            "title": clean_text(title),
                            "url": url or search_url,
                            "author": clean_text(author),
                            "platform": "知乎",
                        })
                except Exception as e:
                    logger.debug(f"解析知乎项失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"知乎搜索失败: {e}")

        logger.info(f"知乎搜索完成，找到 {len(results)} 个内容")
        return results

    async def get_comments(self, url: str, max_count: int = 100) -> List[CommentData]:
        """获取知乎评论"""
        comments = []
        try:
            await self.safe_goto(url)
            await random_delay(5, 8)

            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await random_delay(3, 5)

            title = ""
            try:
                for sel in ['h1', '.QuestionHeader-title', '.Post-Title', 'meta[name="description"]']:
                    try:
                        if sel.startswith('meta'):
                            el = await self.page.query_selector(sel)
                            if el:
                                title = await el.get_attribute("content") or ""
                        else:
                            el = await self.page.query_selector(sel)
                            if el:
                                title = await el.inner_text()
                        if title:
                            break
                    except:
                        continue
            except:
                pass

            # 尝试展开评论
            try:
                comment_toggle = await self.page.query_selector('button:has-text("评论"), .CommentCollapse-button')
                if comment_toggle:
                    await comment_toggle.click()
                    await random_delay(2, 3)
            except:
                pass

            for _ in range(5):
                await self.page.evaluate("window.scrollBy(0, 500)")
                await random_delay(1, 2)

            comment_selectors = [
                '.CommentItemV2',
                '.CommentItem',
                'div[class*="Comment"]',
            ]

            comment_elements = []
            for selector in comment_selectors:
                try:
                    comment_elements = await self.page.query_selector_all(selector)
                    if comment_elements:
                        logger.info(f"知乎评论: 使用选择器 {selector} 找到 {len(comment_elements)} 条")
                        break
                except:
                    continue

            for el in comment_elements[:max_count]:
                try:
                    content = ""
                    for content_sel in ['.CommentItemV2-content', '[class*="content"]', 'p', 'span']:
                        try:
                            content_el = await el.query_selector(content_sel)
                            if content_el:
                                content = await content_el.inner_text()
                                if content and len(content) > 2:
                                    break
                        except:
                            continue

                    author = ""
                    for author_sel in ['.CommentItemV2-meta a', '[class*="name"]', 'a']:
                        try:
                            author_el = await el.query_selector(author_sel)
                            if author_el:
                                author = await author_el.inner_text()
                                if author and len(author) < 20:
                                    break
                        except:
                            continue

                    likes = 0
                    try:
                        likes_el = await el.query_selector('.VoteButton--up, [class*="like"]')
                        if likes_el:
                            likes_text = await likes_el.inner_text()
                            likes = int(re.sub(r'[^\d]', '', likes_text) or "0")
                    except:
                        pass

                    if content:
                        comments.append(CommentData(
                            platform="知乎",
                            title=clean_text(title),
                            content=clean_text(content),
                            author=clean_text(author),
                            time="",
                            url=url,
                            likes=likes,
                        ))
                except Exception as e:
                    logger.debug(f"解析知乎评论失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"获取知乎评论失败: {e}")

        logger.info(f"知乎评论采集完成: {len(comments)} 条")
        return comments
