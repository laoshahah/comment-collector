"""
抖音爬虫 - 简化版，使用搜索结果页
"""
import re
from typing import List
from crawlers.base_crawler import BaseCrawler, CommentData
from utils.logger import logger
from utils.helpers import random_delay, clean_text, format_time


class DouyinCrawler(BaseCrawler):
    """抖音爬虫"""

    def __init__(self):
        super().__init__()
        self.platform_name = "抖音"

    async def search(self, keyword: str, max_pages: int = 5) -> List[dict]:
        """搜索抖音视频"""
        results = []
        try:
            search_url = f"https://www.douyin.com/search/{keyword}?type=video"
            await self.safe_goto(search_url)
            await random_delay(5, 8)

            # 等待页面加载
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await random_delay(3, 5)

            # 尝试多种选择器
            selectors = [
                '[data-e2e="search-card-desc"]',
                '.search-result-card',
                '.video-card',
                'li[class*="search"]',
                'div[class*="video"]',
            ]

            video_items = []
            for selector in selectors:
                try:
                    video_items = await self.page.query_selector_all(selector)
                    if video_items:
                        logger.info(f"抖音: 使用选择器 {selector} 找到 {len(video_items)} 个结果")
                        break
                except:
                    continue

            if not video_items:
                # 尝试获取页面内容
                content = await self.page.content()
                logger.warning(f"抖音: 未找到视频列表，页面长度: {len(content)}")
                return results

            for item in video_items[:20]:  # 限制前20个
                try:
                    # 尝试获取标题
                    title = ""
                    for title_sel in ['a', 'span', 'div[class*="title"]', 'p']:
                        try:
                            el = await item.query_selector(title_sel)
                            if el:
                                text = await el.inner_text()
                                if text and len(text) > 5:
                                    title = text[:100]
                                    break
                        except:
                            continue

                    # 尝试获取链接
                    url = ""
                    try:
                        link_el = await item.query_selector('a[href*="/video/"]')
                        if link_el:
                            url = await link_el.get_attribute("href")
                            if url and not url.startswith("http"):
                                url = "https://www.douyin.com" + url
                    except:
                        pass

                    # 尝试获取作者
                    author = ""
                    for author_sel in ['[class*="author"]', '[class*="nickname"]', 'span']:
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
                            "platform": "抖音",
                        })
                except Exception as e:
                    logger.debug(f"解析抖音项失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"抖音搜索失败: {e}")

        logger.info(f"抖音搜索完成，找到 {len(results)} 个视频")
        return results

    async def get_comments(self, url: str, max_count: int = 100) -> List[CommentData]:
        """获取抖音视频评论"""
        comments = []
        try:
            await self.safe_goto(url)
            await random_delay(5, 8)

            # 等待页面加载
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await random_delay(3, 5)

            # 获取视频标题
            title = ""
            try:
                for sel in ['h1', '[class*="title"]', 'meta[name="description"]']:
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

            # 滚动到评论区
            for _ in range(5):
                await self.page.evaluate("window.scrollBy(0, 500)")
                await random_delay(1, 2)

            # 尝试多种评论选择器
            comment_selectors = [
                '[data-e2e="comment-list"]',
                '[class*="comment"]',
                '[class*="Comment"]',
                'div[class*="comment-item"]',
            ]

            comment_elements = []
            for selector in comment_selectors:
                try:
                    comment_elements = await self.page.query_selector_all(selector)
                    if comment_elements:
                        logger.info(f"抖音评论: 使用选择器 {selector} 找到 {len(comment_elements)} 条")
                        break
                except:
                    continue

            for el in comment_elements[:max_count]:
                try:
                    # 获取评论内容
                    content = ""
                    for content_sel in ['[class*="content"]', '[class*="text"]', 'p', 'span']:
                        try:
                            content_el = await el.query_selector(content_sel)
                            if content_el:
                                content = await content_el.inner_text()
                                if content and len(content) > 2:
                                    break
                        except:
                            continue

                    # 获取作者
                    author = ""
                    for author_sel in ['[class*="author"]', '[class*="name"]', 'a']:
                        try:
                            author_el = await el.query_selector(author_sel)
                            if author_el:
                                author = await author_el.inner_text()
                                if author and len(author) < 20:
                                    break
                        except:
                            continue

                    # 获取点赞数
                    likes = 0
                    try:
                        likes_el = await el.query_selector('[class*="like"], [class*="digg"]')
                        if likes_el:
                            likes_text = await likes_el.inner_text()
                            likes = int(re.sub(r'[^\d]', '', likes_text) or "0")
                    except:
                        pass

                    if content:
                        comments.append(CommentData(
                            platform="抖音",
                            title=clean_text(title),
                            content=clean_text(content),
                            author=clean_text(author),
                            time="",
                            url=url,
                            likes=likes,
                        ))
                except Exception as e:
                    logger.debug(f"解析抖音评论失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"获取抖音评论失败: {e}")

        logger.info(f"抖音评论采集完成: {len(comments)} 条")
        return comments
