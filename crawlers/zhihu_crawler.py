"""
知乎爬虫
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
            await random_delay(3, 5)

            # 等待搜索结果加载
            await self.page.wait_for_selector('.SearchResult-Card, .List-item', timeout=15000)

            for page_num in range(max_pages):
                logger.info(f"知乎搜索 第{page_num + 1}页")

                # 获取内容列表
                items = await self.page.query_selector_all('.SearchResult-Card, .List-item')

                for item in items:
                    try:
                        # 提取标题
                        title_el = await item.query_selector('h2 span, .ContentItem-title a')
                        title = await title_el.inner_text() if title_el else ""

                        # 提取链接
                        link_el = await item.query_selector('a[href*="/question/"], a[href*="/answer/"], a[href*="/article/"]')
                        url = await link_el.get_attribute("href") if link_el else ""
                        if url and not url.startswith("http"):
                            url = "https://www.zhihu.com" + url

                        # 提取作者
                        author_el = await item.query_selector('.AuthorInfo-name, .UserLink-link')
                        author = await author_el.inner_text() if author_el else ""

                        if title and url:
                            results.append({
                                "title": clean_text(title),
                                "url": url,
                                "author": clean_text(author),
                                "platform": "知乎",
                            })
                    except Exception as e:
                        logger.debug(f"解析知乎项失败: {e}")
                        continue

                # 滚动加载下一页
                await self.scroll_and_load(3)
                await random_delay(2, 4)

                # 点击加载更多
                load_more = await self.page.query_selector('button:has-text("加载更多"), .Pagination Button:last-child')
                if load_more:
                    await load_more.click()
                    await random_delay(2, 3)

        except Exception as e:
            logger.error(f"知乎搜索失败: {e}")

        logger.info(f"知乎搜索完成，找到 {len(results)} 个内容")
        return results

    async def get_comments(self, url: str, max_count: int = 100) -> List[CommentData]:
        """获取知乎评论（回答/文章评论）"""
        comments = []
        try:
            await self.safe_goto(url)
            await random_delay(3, 5)

            # 获取标题
            title = ""
            try:
                title_el = await self.page.query_selector('h1, .QuestionHeader-title, .Post-Title')
                title = await title_el.inner_text() if title_el else ""
            except:
                pass

            # 滚动到评论区
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.5)")
            await random_delay(2, 3)

            # 尝试展开评论
            try:
                comment_toggle = await self.page.query_selector('button:has-text("评论"), .CommentCollapse-button')
                if comment_toggle:
                    await comment_toggle.click()
                    await random_delay(2, 3)
            except:
                pass

            # 等待评论区加载
            await self.page.wait_for_selector('.CommentList, .CommentItemV2', timeout=15000)

            # 滚动加载评论
            for scroll_round in range(10):
                await self.scroll_and_load(2)
                await random_delay(1, 3)

                comment_elements = await self.page.query_selector_all('.CommentItemV2, .CommentItem')
                if len(comment_elements) >= max_count:
                    break

            # 解析评论
            comment_elements = await self.page.query_selector_all('.CommentItemV2, .CommentItem')

            for el in comment_elements[:max_count]:
                try:
                    # 评论内容
                    content_el = await el.query_selector('.CommentItemV2-content, .CommentItem-content')
                    content = await content_el.inner_text() if content_el else ""

                    # 评论作者
                    author_el = await el.query_selector('.CommentItemV2-meta a, .CommentItem-meta a')
                    author = await author_el.inner_text() if author_el else ""

                    # 点赞数
                    likes_el = await el.query_selector('.VoteButton--up, .CommentItem-like')
                    likes_text = await likes_el.inner_text() if likes_el else "0"
                    likes = int(re.sub(r'[^\d]', '', likes_text) or "0")

                    # 时间
                    time_el = await el.query_selector('.CommentItemV2-time, .CommentItem-time')
                    time_str = await time_el.inner_text() if time_el else ""

                    if content:
                        comment = CommentData(
                            platform="知乎",
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
            logger.error(f"获取知乎评论失败: {e}")

        logger.info(f"知乎评论采集完成: {len(comments)} 条")
        return comments
