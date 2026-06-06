"""
微博爬虫
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
            await random_delay(3, 5)

            # 等待搜索结果加载
            await self.page.wait_for_selector('.card-wrap, .card', timeout=15000)

            for page_num in range(max_pages):
                logger.info(f"微博搜索 第{page_num + 1}页")

                # 获取微博列表
                weibo_items = await self.page.query_selector_all('.card-wrap:not([mid=""]), .card[action-type="feed_list_item"]')

                for item in weibo_items:
                    try:
                        # 提取内容（微博没有单独标题，用内容前50字作为标题）
                        content_el = await item.query_selector('.txt, .weibo-text')
                        content = await content_el.inner_text() if content_el else ""
                        title = content[:50] + "..." if len(content) > 50 else content

                        # 提取链接
                        link_el = await item.query_selector('a[href*="/detail/"], .card-act a:first-child')
                        url = await link_el.get_attribute("href") if link_el else ""
                        if url and not url.startswith("http"):
                            url = "https://weibo.com" + url

                        # 提取作者
                        author_el = await item.query_selector('.name, .card-name')
                        author = await author_el.inner_text() if author_el else ""

                        if content and url:
                            results.append({
                                "title": clean_text(title),
                                "url": url,
                                "author": clean_text(author),
                                "platform": "微博",
                            })
                    except Exception as e:
                        logger.debug(f"解析微博项失败: {e}")
                        continue

                # 滚动加载下一页
                await self.scroll_and_load(3)
                await random_delay(2, 4)

                # 点击下一页
                next_btn = await self.page.query_selector('.page.next, a:has-text("下一页")')
                if next_btn:
                    await next_btn.click()
                    await random_delay(2, 3)

        except Exception as e:
            logger.error(f"微博搜索失败: {e}")

        logger.info(f"微博搜索完成，找到 {len(results)} 条微博")
        return results

    async def get_comments(self, url: str, max_count: int = 100) -> List[CommentData]:
        """获取微博评论"""
        comments = []
        try:
            await self.safe_goto(url)
            await random_delay(3, 5)

            # 获取微博内容作为标题
            title = ""
            try:
                content_el = await self.page.query_selector('.txt, .weibo-text')
                content = await content_el.inner_text() if content_el else ""
                title = content[:50] + "..." if len(content) > 50 else content
            except:
                pass

            # 滚动到评论区
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
            await random_delay(2, 3)

            # 等待评论区加载
            await self.page.wait_for_selector('.comment-list, .comment-content', timeout=15000)

            # 滚动加载评论
            for scroll_round in range(10):
                await self.scroll_and_load(2)
                await random_delay(1, 3)

                comment_elements = await self.page.query_selector_all('.comment-item, .comment-content')
                if len(comment_elements) >= max_count:
                    break

            # 解析评论
            comment_elements = await self.page.query_selector_all('.comment-item, .comment-content')

            for el in comment_elements[:max_count]:
                try:
                    # 评论内容
                    content_el = await el.query_selector('.txt, .comment-text')
                    content = await content_el.inner_text() if content_el else ""

                    # 评论作者
                    author_el = await el.query_selector('.name, .comment-name')
                    author = await author_el.inner_text() if author_el else ""

                    # 点赞数
                    likes_el = await el.query_selector('.like-count, .comment-like')
                    likes_text = await likes_el.inner_text() if likes_el else "0"
                    likes = int(re.sub(r'[^\d]', '', likes_text) or "0")

                    # 时间
                    time_el = await el.query_selector('.time, .comment-time')
                    time_str = await time_el.inner_text() if time_el else ""

                    if content:
                        comment = CommentData(
                            platform="微博",
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
            logger.error(f"获取微博评论失败: {e}")

        logger.info(f"微博评论采集完成: {len(comments)} 条")
        return comments
