"""
简化爬虫 - 从搜索结果页直接提取数据
无需登录，无需进入详情页
"""
import re
from typing import List
from crawlers.base_crawler import BaseCrawler, CommentData
from utils.logger import logger
from utils.helpers import random_delay, clean_text


class SimpleCrawler(BaseCrawler):
    """简化爬虫 - 从搜索结果提取数据"""

    def __init__(self, platform_name: str, search_url: str):
        super().__init__()
        self.platform_name = platform_name
        self.search_url_template = search_url

    async def search(self, keyword: str, max_pages: int = 5) -> List[dict]:
        """搜索并提取搜索结果中的可见信息"""
        results = []
        try:
            search_url = self.search_url_template.format(keyword=keyword)
            await self.safe_goto(search_url)
            await random_delay(5, 8)

            # 等待页面加载
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await random_delay(3, 5)

            # 获取页面所有文本内容
            page_content = await self.page.content()

            # 提取所有可见文本
            text_elements = await self.page.query_selector_all('h1, h2, h3, p, span, div, a, li')

            for el in text_elements:
                try:
                    text = await el.inner_text()
                    if text and len(text) > 10:
                        # 提取手机号
                        phone_match = re.search(r'1[3-9]\d{9}', text)
                        # 提取微信号
                        wechat_match = re.search(r'[Vv][Xx微信][:：\s]*([a-zA-Z0-9_]{5,20})', text)
                        # 提取QQ号
                        qq_match = re.search(r'[Qq]{2}[:：\s]*([1-9]\d{4,11})', text)
                        # 提取邮箱
                        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

                        # 检查是否包含联系方式或需求关键词
                        has_contact = phone_match or wechat_match or qq_match or email_match
                        intent_keywords = ['多少钱', '怎么买', '链接', '价格', '加盟', '联系方式', '教程', '想要', '求']
                        has_intent = any(kw in text for kw in intent_keywords)

                        if has_contact or has_intent:
                            # 尝试获取链接
                            url = ""
                            try:
                                url = await el.get_attribute("href") or ""
                                if url and not url.startswith("http"):
                                    url = f"https://www.{self.platform_name.lower()}.com" + url
                            except:
                                pass

                            results.append({
                                "title": text[:50] + "..." if len(text) > 50 else text,
                                "content": text,
                                "url": url or search_url,
                                "platform": self.platform_name,
                                "phone": phone_match.group(0) if phone_match else "",
                                "wechat": wechat_match.group(1) if wechat_match else "",
                                "qq": qq_match.group(1) if qq_match else "",
                                "email": email_match.group(0) if email_match else "",
                            })
                except:
                    continue

            logger.info(f"{self.platform_name}: 从搜索结果提取了 {len(results)} 条有效信息")

        except Exception as e:
            logger.error(f"{self.platform_name} 搜索失败: {e}")

        return results

    async def get_comments(self, url: str, max_count: int = 100) -> List[CommentData]:
        """获取评论（简化版，直接从页面提取）"""
        comments = []
        try:
            await self.safe_goto(url)
            await random_delay(5, 8)

            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await random_delay(3, 5)

            # 获取页面所有文本
            text_elements = await self.page.query_selector_all('p, span, div, li, td')

            for el in text_elements[:max_count]:
                try:
                    text = await el.inner_text()
                    if text and len(text) > 5:
                        # 提取联系方式
                        phone = re.search(r'1[3-9]\d{9}', text)
                        wechat = re.search(r'[Vv][Xx微信][:：\s]*([a-zA-Z0-9_]{5,20})', text)
                        qq = re.search(r'[Qq]{2}[:：\s]*([1-9]\d{4,11})', text)
                        email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

                        if phone or wechat or qq or email:
                            comments.append(CommentData(
                                platform=self.platform_name,
                                title="",
                                content=clean_text(text),
                                author="",
                                time="",
                                url=url,
                                phone=phone.group(0) if phone else "",
                                wechat=wechat.group(1) if wechat else "",
                                qq=qq.group(1) if qq else "",
                                email=email.group(0) if email else "",
                            ))
                except:
                    continue

            logger.info(f"{self.platform_name}: 提取了 {len(comments)} 条包含联系方式的评论")

        except Exception as e:
            logger.error(f"{self.platform_name} 评论提取失败: {e}")

        return comments
