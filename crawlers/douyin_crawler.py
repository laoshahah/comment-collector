"""
抖音爬虫
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
            await random_delay(3, 5)

            # 等待搜索结果加载
            await self.page.wait_for_selector('[class*="search-result"]', timeout=15000)

            for page_num in range(max_pages):
                logger.info(f"抖音搜索 第{page_num + 1}页")

                # 获取视频列表
                video_items = await self.page.query_selector_all('[class*="video-card"], [class*="search-result-card"]')

                for item in video_items:
                    try:
                        # 提取标题
                        title_el = await item.query_selector('[class*="title"], a')
                        title = await title_el.inner_text() if title_el else ""

                        # 提取链接
                        link_el = await item.query_selector('a[href*="/video/"]')
                        url = await link_el.get_attribute("href") if link_el else ""
                        if url and not url.startswith("http"):
                            url = "https://www.douyin.com" + url

                        # 提取作者
                        author_el = await item.query_selector('[class*="author"], [class*="nickname"]')
                        author = await author_el.inner_text() if author_el else ""

                        if title and url:
                            results.append({
                                "title": clean_text(title),
                                "url": url,
                                "author": clean_text(author),
                                "platform": "抖音",
                            })
                    except Exception as e:
                        logger.debug(f"解析视频项失败: {e}")
                        continue

                # 滚动加载下一页
                await self.scroll_and_load(3)
                await random_delay(2, 4)

        except Exception as e:
            logger.error(f"抖音搜索失败: {e}")

        logger.info(f"抖音搜索完成，找到 {len(results)} 个视频")
        return results

    async def get_comments(self, url: str, max_count: int = 100) -> List[CommentData]:
        """获取抖音视频评论"""
        comments = []
        try:
            await self.safe_goto(url)
            await random_delay(3, 5)

            # 获取视频标题
            title = ""
            try:
                title_el = await self.page.query_selector('[class*="title"], h1')
                title = await title_el.inner_text() if title_el else ""
            except:
                pass

            # 等待评论区加载
            await self.page.wait_for_selector('[class*="comment"], [class*="Comment"]', timeout=15000)

            # 滚动加载评论
            for scroll_round in range(10):
                await self.scroll_and_load(2)
                await random_delay(1, 3)

                # 检查是否达到最大评论数
                comment_elements = await self.page.query_selector_all('[class*="comment-item"], [class*="CommentItem"]')
                if len(comment_elements) >= max_count:
                    break

            # 解析评论
            comment_elements = await self.page.query_selector_all('[class*="comment-item"], [class*="CommentItem"]')

            for i, el in enumerate(comment_elements[:max_count]):
                try:
                    # 评论内容
                    content_el = await el.query_selector('[class*="content"], [class*="text"], p')
                    content = await content_el.inner_text() if content_el else ""

                    # 评论作者
                    author_el = await el.query_selector('[class*="author"], [class*="nickname"], [class*="name"]')
                    author = await author_el.inner_text() if author_el else ""

                    # 点赞数
                    likes_el = await el.query_selector('[class*="like"], [class*="digg"]')
                    likes_text = await likes_el.inner_text() if likes_el else "0"
                    likes = int(re.sub(r'[^\d]', '', likes_text) or "0")

                    # 时间
                    time_el = await el.query_selector('[class*="time"], [class*="date"]')
                    time_str = await time_el.inner_text() if time_el else ""

                    if content:
                        comment = CommentData(
                            platform="抖音",
                            title=clean_text(title),
                            content=clean_text(content),
                            author=clean_text(author),
                            time=format_time(time_str),
                            url=url,
                            likes=likes,
                        )
                        comments.append(comment)

                except Exception as e:
                    logger.debug(f"解析评论失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"获取抖音评论失败: {e}")

        logger.info(f"抖音评论采集完成: {len(comments)} 条")
        return comments
