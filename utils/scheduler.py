"""
定时任务调度器
支持定时自动爬取
"""
import json
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional
from pathlib import Path
from config import PROJECT_ROOT
from utils.logger import logger


# 定时任务配置文件
SCHEDULE_FILE = PROJECT_ROOT / "schedules.json"


class ScheduledTask:
    """定时任务"""

    def __init__(self, task_id: int, keyword: str, platforms: List[str],
                 schedule_type: str = "daily", schedule_time: str = "09:00",
                 enabled: bool = True, last_run: str = None):
        self.task_id = task_id
        self.keyword = keyword
        self.platforms = platforms
        self.schedule_type = schedule_type  # daily, weekly, hourly
        self.schedule_time = schedule_time  # HH:MM 格式
        self.enabled = enabled
        self.last_run = last_run

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "keyword": self.keyword,
            "platforms": self.platforms,
            "schedule_type": self.schedule_type,
            "schedule_time": self.schedule_time,
            "enabled": self.enabled,
            "last_run": self.last_run,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduledTask':
        """从字典创建"""
        return cls(
            task_id=data.get("task_id", 0),
            keyword=data.get("keyword", ""),
            platforms=data.get("platforms", []),
            schedule_type=data.get("schedule_type", "daily"),
            schedule_time=data.get("schedule_time", "09:00"),
            enabled=data.get("enabled", True),
            last_run=data.get("last_run"),
        )

    def should_run(self) -> bool:
        """检查是否应该运行"""
        if not self.enabled:
            return False

        now = datetime.now()

        # 解析计划时间
        hour, minute = map(int, self.schedule_time.split(":"))
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # 检查是否已运行过
        if self.last_run:
            last_run_time = datetime.fromisoformat(self.last_run)
            if self.schedule_type == "daily":
                # 每天任务：如果今天已运行过，跳过
                if last_run_time.date() == now.date():
                    return False
            elif self.schedule_type == "hourly":
                # 每小时任务：如果最近一小时内运行过，跳过
                if now - last_run_time < timedelta(hours=1):
                    return False

        # 检查是否到达计划时间
        if self.schedule_type == "daily":
            return now >= scheduled_time
        elif self.schedule_type == "hourly":
            return True  # 每小时任务总是检查
        elif self.schedule_type == "weekly":
            # 每周任务：只在周一运行
            return now.weekday() == 0 and now >= scheduled_time

        return False


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.tasks: List[ScheduledTask] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None
        self.load_tasks()

    def load_tasks(self):
        """加载定时任务"""
        try:
            if SCHEDULE_FILE.exists():
                with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = [ScheduledTask.from_dict(t) for t in data.get("tasks", [])]
                logger.info(f"加载了 {len(self.tasks)} 个定时任务")
        except Exception as e:
            logger.error(f"加载定时任务失败: {e}")

    def save_tasks(self):
        """保存定时任务"""
        try:
            data = {
                "tasks": [t.to_dict() for t in self.tasks]
            }
            with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存了 {len(self.tasks)} 个定时任务")
        except Exception as e:
            logger.error(f"保存定时任务失败: {e}")

    def add_task(self, keyword: str, platforms: List[str],
                 schedule_type: str = "daily", schedule_time: str = "09:00") -> ScheduledTask:
        """添加定时任务"""
        task_id = max([t.task_id for t in self.tasks], default=0) + 1
        task = ScheduledTask(
            task_id=task_id,
            keyword=keyword,
            platforms=platforms,
            schedule_type=schedule_type,
            schedule_time=schedule_time,
        )
        self.tasks.append(task)
        self.save_tasks()
        logger.info(f"添加定时任务: {keyword} ({schedule_type} {schedule_time})")
        return task

    def remove_task(self, task_id: int):
        """删除定时任务"""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
        self.save_tasks()
        logger.info(f"删除定时任务: {task_id}")

    def update_task(self, task_id: int, **kwargs):
        """更新定时任务"""
        for task in self.tasks:
            if task.task_id == task_id:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                break
        self.save_tasks()

    def get_tasks(self) -> List[ScheduledTask]:
        """获取所有任务"""
        return self.tasks

    def start(self, callback: Callable):
        """启动调度器"""
        self.callback = callback
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("定时任务调度器已启动")

    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("定时任务调度器已停止")

    def _run(self):
        """调度器主循环"""
        while self.running:
            try:
                # 检查所有任务
                for task in self.tasks:
                    if task.should_run():
                        logger.info(f"执行定时任务: {task.keyword}")
                        if self.callback:
                            self.callback(task)
                        task.last_run = datetime.now().isoformat()
                        self.save_tasks()

                # 每分钟检查一次
                time.sleep(60)
            except Exception as e:
                logger.error(f"调度器错误: {e}")
                time.sleep(60)
