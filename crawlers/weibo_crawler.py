"""
微博爬虫 - 简化版
"""
import re
from typing import List
from crawlers.base_crawler import BaseCrawler, CommentData
from utils.logger import logger
from utils.helpers import random_delay, clean_text, format_time


class WeiboCrawler(BaseCrawler):
    """微博爬虫"""

    def __init__(self):
        super().__init__()
        self.platform_name = "微博"

    async def search(self, keyword: str, max_pages: int = 5) -> List[dict]:
        """搜索微博"""
        results = []
        try:
            search_url = f"https://s.weibo.com/weibo?q={keyword}"
            await self.safe_goto(search_url)
            await random_delay(5, 8)

            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await random_delay(3, 5)

            selectors = [
                '.card-wrap',
                '.card',
                'div[class*="weibo"]',
                'div[class*="item"]',
            ]

            weibo_items = []
            for selector in selectors:
                try:
                    weibo_items = await self.page.query_selector_all(selector)
                    if weibo_items:
                        logger.info(f"微博: 使用选择器 {selector} 找到 {len(weibo_items)} 个结果")
                        break
                except:
                    continue

            if not weibo_items:
                content = await self.page.content()
                logger.warning(f"微博: 未找到微博列表，页面长度: {len(content)}")
                return results

            for item in weibo_items[:20]:
                try:
                    # 微博内容作为标题
                    content_text = ""
                    for content_sel in ['.txt', '[class*="text"]', 'p']:
                        try:
                            el = await item.query_selector(content_sel)
                            if el:
                                text = await el.inner_text()
                                if text and len(text) > 10:
                                    content_text = text[:100]
                                    break
                        except:
                            continue

                    title = content_text[:50] + "..." if len(content_text) > 50 else content_text

                    url = ""
                    try:
                        link_el = await item.query_selector('a[href*="/detail/"], a[href*="/status/"]')
                        if link_el:
                            url = await link_el.get_attribute("href")
                            if url and not url.startswith("http"):
                                url = "https://weibo.com" + url
                    except:
                        pass

                    author = ""
                    for author_sel in ['.name', '[class*="name"]', 'a']:
                        try:
                            el = await item.query_selector(author_sel)
                            if el:
                                text = await el.inner_text()
                                if text and len(text) < 20:
                                    author = text
                                    break
                        except:
                            continue

                    if content_text:
                        results.append({
                            "title": clean_text(title),
                            "url": url or search_url,
                            "author": clean_text(author),
                            "platform": "微博",
                        })
                except Exception as e:
                    logger.debug(f"解析微博项失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"微博搜索失败: {e}")

        logger.info(f"微博搜索完成，找到 {len(results)} 条微博")
        return results

    async def get_comments(self, url: str, max_count: int = 100) -> List[CommentData]:
        """获取微博评论"""
        comments = []
        try:
            await self.safe_goto(url)
            await random_delay(5, 8)

            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await random_delay(3, 5)

            title = ""
            try:
                for sel in ['.txt', '[class*="text"]', 'meta[name="description"]']:
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
                            title = title[:50]
                            break
                    except:
                        continue
            except:
                pass

            for _ in range(5):
                await self.page.evaluate("window.scrollBy(0, 500)")
                await random_delay(1, 2)

            comment_selectors = [
                '.comment-item',
                '[class*="comment"]',
                'div[class*="Comment"]',
            ]

            comment_elements = []
            for selector in comment_selectors:
                try:
                    comment_elements = await self.page.query_selector_all(selector)
                    if comment_elements:
                        logger.info(f"微博评论: 使用选择器 {selector} 找到 {len(comment_elements)} 条")
                        break
                except:
                    continue

            for el in comment_elements[:max_count]:
                try:
                    content = ""
                    for content_sel in ['.txt', '[class*="text"]', 'p', 'span']:
                        try:
                            content_el = await el.query_selector(content_sel)
                            if content_el:
                                content = await content_el.inner_text()
                                if content and len(content) > 2:
                                    break
                        except:
                            continue

                    author = ""
                    for author_sel in ['.name', '[class*="name"]', 'a']:
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
                        likes_el = await el.query_selector('[class*="like"]')
                        if likes_el:
                            likes_text = await likes_el.inner_text()
                            likes = int(re.sub(r'[^\d]', '', likes_text) or "0")
                    except:
                        pass

                    if content:
                        comments.append(CommentData(
                            platform="微博",
                            title=clean_text(title),
                            content=clean_text(content),
                            author=clean_text(author),
                            time="",
                            url=url,
                            likes=likes,
                        ))
                except Exception as e:
                    logger.debug(f"解析微博评论失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"获取微博评论失败: {e}")

        logger.info(f"微博评论采集完成: {len(comments)} 条")
        return comments
