# 数据获取策略详解: 原神游戏信息网站

## 数据源架构概览

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   哔哩哔哩Wiki    │    │   玉衡杯数据库     │    │   原神官方       │
│   基础游戏信息    │    │   精确数值数据     │    │   图片和最新信息  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     数据同步和合并服务                            │
├─────────────────────────────────────────────────────────────────┤
│  • 冲突解决策略                                                  │
│  • 数据质量验证                                                  │
│  • 增量更新机制                                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL 数据库                          │
│  Character | Weapon | Artifact | Monster | GameMechanic         │
└─────────────────────────────────────────────────────────────────┘
```

## 1. 哔哩哔哩Wiki数据获取

### 实现方案
```python
# backend/src/scrapers/bilibili_scraper.py
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import asyncio
from urllib.parse import urljoin

class BilibiliWikiScraper:
    def __init__(self):
        self.base_url = "https://wiki.biligame.com/ys"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://wiki.biligame.com/ys/'
        }

    async def fetch_characters(self) -> List[Dict]:
        """获取所有角色基础信息"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # 1. 获取角色列表页面
            characters_url = f"{self.base_url}/角色"
            characters = []

            async with session.get(characters_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # 2. 解析角色列表
                character_links = soup.find_all('a', href=True)
                character_urls = []

                for link in character_links:
                    href = link.get('href')
                    if href and '/角色/' in href:
                        full_url = urljoin(self.base_url, href)
                        character_urls.append(full_url)

                # 3. 并发获取每个角色详情
                tasks = [self._fetch_character_detail(session, url)
                        for url in character_urls[:10]]  # 限制并发数

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in results:
                    if isinstance(result, dict):
                        characters.append(result)
                    else:
                        print(f"Error fetching character: {result}")

            return characters

    async def _fetch_character_detail(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """获取单个角色的详细信息"""
        try:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                character_data = {
                    'name': self._extract_character_name(soup),
                    'element': self._extract_element(soup),
                    'weapon_type': self._extract_weapon_type(soup),
                    'rarity': self._extract_rarity(soup),
                    'region': self._extract_region(soup),
                    'description': self._extract_description(soup),
                    'base_stats': self._extract_base_stats(soup),
                    'skills': await self._extract_skills(session, soup),
                    'talents': self._extract_talents(soup),
                    'source_url': url,
                    'last_updated': datetime.utcnow().isoformat()
                }

                return character_data

        except Exception as e:
            print(f"Error parsing character from {url}: {e}")
            return None

    def _extract_character_name(self, soup: BeautifulSoup) -> str:
        """提取角色名称"""
        # 查找页面标题或特定的角色名称元素
        title_elem = soup.find('h1', class_='firstHeading')
        if title_elem:
            return title_elem.get_text().strip()

        # 备用方案：从页面标题提取
        title = soup.find('title')
        if title:
            name = title.get_text().replace(' - 原神WIKI_BWIKI_哔哩哔哩', '')
            return name.strip()

        return "Unknown"

    def _extract_element(self, soup: BeautifulSoup) -> Optional[str]:
        """提取元素类型"""
        # 查找元素图标或文本
        element_patterns = {
            '风': 'Anemo', '岩': 'Geo', '雷': 'Electro',
            '草': 'Dendro', '水': 'Hydro', '火': 'Pyro', '冰': 'Cryo'
        }

        # 在信息框中查找元素信息
        info_box = soup.find('table', class_='infobox')
        if info_box:
            text = info_box.get_text()
            for cn_element, en_element in element_patterns.items():
                if cn_element in text:
                    return en_element

        return None

    def _extract_weapon_type(self, soup: BeautifulSoup) -> Optional[str]:
        """提取武器类型"""
        weapon_patterns = {
            '单手剑': 'Sword', '双手剑': 'Claymore', '长柄武器': 'Polearm',
            '弓': 'Bow', '法器': 'Catalyst'
        }

        info_box = soup.find('table', class_='infobox')
        if info_box:
            text = info_box.get_text()
            for cn_weapon, en_weapon in weapon_patterns.items():
                if cn_weapon in text:
                    return en_weapon

        return None

    def _extract_base_stats(self, soup: BeautifulSoup) -> Dict:
        """提取基础属性"""
        stats = {'hp': 0, 'atk': 0, 'def': 0}

        # 查找属性表格
        stats_table = soup.find('table', string=lambda text: text and '基础生命值' in text)
        if not stats_table:
            # 尝试其他可能的表格结构
            stats_table = soup.find('table', class_='wikitable')

        if stats_table:
            rows = stats_table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    stat_name = cells[0].get_text().strip()
                    stat_value = cells[1].get_text().strip()

                    # 提取数值
                    import re
                    numbers = re.findall(r'\d+', stat_value)
                    if numbers:
                        value = int(numbers[0])

                        if '生命值' in stat_name or 'HP' in stat_name:
                            stats['hp'] = value
                        elif '攻击力' in stat_name or 'ATK' in stat_name:
                            stats['atk'] = value
                        elif '防御力' in stat_name or 'DEF' in stat_name:
                            stats['def'] = value

        return stats

    async def fetch_weapons(self) -> List[Dict]:
        """获取武器信息"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            weapons_url = f"{self.base_url}/武器"
            weapons = []

            async with session.get(weapons_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # 实现武器解析逻辑...

            return weapons

    async def fetch_artifacts(self) -> List[Dict]:
        """获取圣遗物信息"""
        # 实现圣遗物解析逻辑...
        pass
```

### 获取策略
- **反爬虫应对**: 随机User-Agent，请求间隔，IP轮换
- **数据质量**: 多重验证，异常数据标记
- **增量更新**: 基于页面修改时间的智能更新

## 2. 玉衡杯数据库获取

### 实现方案
```python
# backend/src/scrapers/homdgcat_scraper.py
import aiohttp
import json
from typing import Dict, List

class HomdgcatScraper:
    def __init__(self):
        self.base_url = "https://homdgcat.wiki/gi"
        self.api_endpoints = {
            'characters': '/api/characters',
            'weapons': '/api/weapons',
            'artifacts': '/api/artifacts'
        }

    async def fetch_character_data(self) -> List[Dict]:
        """从玉衡杯获取角色数值数据"""
        async with aiohttp.ClientSession() as session:
            # 尝试API方式
            try:
                api_url = f"{self.base_url}{self.api_endpoints['characters']}"
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_character_api_data(data)
            except:
                pass

            # 降级到网页爬虫方式
            return await self._scrape_character_pages(session)

    async def _scrape_character_pages(self, session: aiohttp.ClientSession) -> List[Dict]:
        """网页爬虫方式获取角色数据"""
        characters = []

        # 获取角色列表页面
        char_list_url = f"{self.base_url}/char"
        async with session.get(char_list_url) as response:
            html = await response.text()

            # 使用正则表达式或BeautifulSoup解析页面中的JSON数据
            import re
            json_pattern = r'window\.__INITIAL_DATA__\s*=\s*(\{.*?\});'
            match = re.search(json_pattern, html, re.DOTALL)

            if match:
                try:
                    data = json.loads(match.group(1))
                    characters = self._extract_characters_from_page_data(data)
                except json.JSONDecodeError:
                    pass

        return characters

    def _extract_characters_from_page_data(self, data: Dict) -> List[Dict]:
        """从页面数据中提取角色信息"""
        characters = []

        # 根据实际的数据结构解析
        if 'characters' in data:
            for char_data in data['characters']:
                character = {
                    'name': char_data.get('name'),
                    'scaling_data': char_data.get('skills', {}),
                    'stats_growth': char_data.get('stats', {}),
                    'talent_levels': char_data.get('talents', {}),
                    'source': 'homdgcat'
                }
                characters.append(character)

        return characters
```

## 3. 官方数据获取

### 实现方案
```python
# backend/src/scrapers/official_scraper.py
import aiohttp
from typing import List, Dict

class OfficialGenshinScraper:
    def __init__(self):
        self.official_api = "https://sg-hk4e-api.hoyoverse.com"  # 示例API
        self.official_web = "https://genshin.hoyoverse.com"

    async def fetch_official_images(self) -> List[Dict]:
        """获取官方角色图片"""
        async with aiohttp.ClientSession() as session:
            images = []

            # 尝试官方API
            try:
                api_url = f"{self.official_api}/common/gacha_config/list"
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        images.extend(self._extract_images_from_api(data))
            except:
                pass

            # 爬取官网图片
            web_images = await self._scrape_official_website(session)
            images.extend(web_images)

            return images

    async def _scrape_official_website(self, session: aiohttp.ClientSession) -> List[Dict]:
        """从官网爬取图片"""
        images = []

        # 角色页面
        characters_url = f"{self.official_web}/zh-cn/character"
        async with session.get(characters_url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # 查找高清图片
            img_tags = soup.find_all('img', src=True)
            for img in img_tags:
                src = img.get('src')
                if src and any(keyword in src.lower() for keyword in ['character', 'portrait', 'card']):
                    images.append({
                        'url': src,
                        'type': 'official',
                        'entity_type': 'character',
                        'source': 'official_website'
                    })

        return images
```

## 4. 数据合并和冲突解决

### 实现方案
```python
# backend/src/services/data_sync_service.py
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

class DataSyncService:
    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client
        self.bilibili_scraper = BilibiliWikiScraper()
        self.homdgcat_scraper = HomdgcatScraper()
        self.official_scraper = OfficialGenshinScraper()

    async def sync_all_data(self) -> Dict:
        """同步所有数据源"""
        sync_results = {
            'characters': {'added': 0, 'updated': 0, 'errors': 0},
            'weapons': {'added': 0, 'updated': 0, 'errors': 0},
            'artifacts': {'added': 0, 'updated': 0, 'errors': 0},
            'images': {'added': 0, 'updated': 0, 'errors': 0}
        }

        try:
            # 并发获取所有数据源
            bilibili_data, homdgcat_data, official_data = await asyncio.gather(
                self._fetch_bilibili_data(),
                self._fetch_homdgcat_data(),
                self._fetch_official_data(),
                return_exceptions=True
            )

            # 合并角色数据
            characters_result = await self._merge_character_data(
                bilibili_data.get('characters', []),
                homdgcat_data.get('characters', [])
            )
            sync_results['characters'] = characters_result

            # 合并武器数据
            weapons_result = await self._merge_weapon_data(
                bilibili_data.get('weapons', []),
                homdgcat_data.get('weapons', [])
            )
            sync_results['weapons'] = weapons_result

            # 处理官方图片
            images_result = await self._process_official_images(
                official_data.get('images', [])
            )
            sync_results['images'] = images_result

        except Exception as e:
            print(f"Sync error: {e}")

        return sync_results

    async def _merge_character_data(self, bilibili_chars: List[Dict], homdgcat_chars: List[Dict]) -> Dict:
        """合并角色数据，解决冲突"""
        result = {'added': 0, 'updated': 0, 'errors': 0}

        # 创建homdgcat数据的索引
        homdgcat_index = {char['name']: char for char in homdgcat_chars if char.get('name')}

        for bili_char in bilibili_chars:
            try:
                char_name = bili_char.get('name')
                if not char_name:
                    continue

                # 查找对应的homdgcat数据
                homdg_char = homdgcat_index.get(char_name)

                # 合并数据 - 哔哩哔哩为基础，homdgcat补充数值
                merged_char = self._merge_character_info(bili_char, homdg_char)

                # 检查数据库中是否已存在
                existing_char = await self._get_existing_character(char_name)

                if existing_char:
                    # 更新现有角色
                    if await self._should_update_character(existing_char, merged_char):
                        await self._update_character(existing_char.id, merged_char)
                        result['updated'] += 1
                else:
                    # 创建新角色
                    await self._create_character(merged_char)
                    result['added'] += 1

            except Exception as e:
                print(f"Error processing character {bili_char.get('name', 'Unknown')}: {e}")
                result['errors'] += 1

        return result

    def _merge_character_info(self, bili_char: Dict, homdg_char: Optional[Dict]) -> Dict:
        """合并单个角色信息"""
        merged = bili_char.copy()

        if homdg_char:
            # homdgcat的数值数据更准确，优先使用
            if homdg_char.get('scaling_data'):
                merged['skills_scaling'] = homdg_char['scaling_data']

            if homdg_char.get('stats_growth'):
                merged['stats_growth'] = homdg_char['stats_growth']

            # 合并天赋等级数据
            if homdg_char.get('talent_levels'):
                merged['talent_levels'] = homdg_char['talent_levels']

        # 添加数据来源标记
        merged['data_sources'] = {
            'bilibili': True,
            'homdgcat': bool(homdg_char),
            'last_synced': datetime.utcnow().isoformat()
        }

        return merged

    async def _should_update_character(self, existing: Any, new_data: Dict) -> bool:
        """判断是否需要更新角色数据"""
        # 比较更新时间
        if existing.updated_at:
            last_sync = new_data.get('data_sources', {}).get('last_synced')
            if last_sync:
                sync_time = datetime.fromisoformat(last_sync)
                if sync_time <= existing.updated_at:
                    return False

        # 检查关键字段是否有变化
        key_fields = ['base_stats', 'skills', 'talents', 'description']
        for field in key_fields:
            if new_data.get(field) != getattr(existing, field, None):
                return True

        return False
```

## 5. 定时同步任务

### Celery任务配置
```python
# backend/src/services/sync_tasks.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery('genshin_sync')

@celery_app.task(bind=True, max_retries=3)
async def sync_characters_task(self):
    """同步角色数据任务"""
    try:
        sync_service = DataSyncService()
        result = await sync_service.sync_character_data()

        # 记录同步结果
        await log_sync_result('characters', result)

        return result
    except Exception as e:
        print(f"Character sync failed: {e}")
        raise self.retry(countdown=60 * 5)  # 5分钟后重试

@celery_app.task
async def sync_all_data_task():
    """完整数据同步任务"""
    sync_service = DataSyncService()
    return await sync_service.sync_all_data()

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每天凌晨2点同步所有数据
    'daily-full-sync': {
        'task': 'sync_all_data_task',
        'schedule': crontab(hour=2, minute=0),
    },
    # 每4小时同步角色数据
    'hourly-character-sync': {
        'task': 'sync_characters_task',
        'schedule': crontab(minute=0, hour='*/4'),
    },
    # 每小时同步官方图片
    'hourly-image-sync': {
        'task': 'sync_official_images_task',
        'schedule': crontab(minute=30),
    },
}
```

## 6. 数据质量监控

### 监控指标
```python
# backend/src/utils/sync_monitor.py
class SyncMonitor:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def record_sync_metrics(self, source: str, metrics: Dict):
        """记录同步指标"""
        timestamp = datetime.utcnow().isoformat()

        # 存储到Redis，保留7天数据
        key = f"sync_metrics:{source}:{timestamp}"
        await self.redis.setex(key, 86400 * 7, json.dumps(metrics))

        # 更新实时统计
        stats_key = f"sync_stats:{source}"
        await self.redis.hset(stats_key, mapping={
            'last_sync': timestamp,
            'total_records': metrics.get('total', 0),
            'success_rate': metrics.get('success_rate', 0),
            'error_count': metrics.get('errors', 0)
        })

    async def check_data_freshness(self) -> Dict:
        """检查数据新鲜度"""
        sources = ['bilibili', 'homdgcat', 'official']
        freshness_report = {}

        for source in sources:
            stats_key = f"sync_stats:{source}"
            last_sync = await self.redis.hget(stats_key, 'last_sync')

            if last_sync:
                sync_time = datetime.fromisoformat(last_sync)
                hours_ago = (datetime.utcnow() - sync_time).total_seconds() / 3600

                freshness_report[source] = {
                    'last_sync': last_sync,
                    'hours_ago': hours_ago,
                    'status': 'fresh' if hours_ago < 6 else 'stale'
                }
            else:
                freshness_report[source] = {'status': 'never_synced'}

        return freshness_report
```

## 7. 数据获取最佳实践

### 性能优化
- **并发控制**: 限制同时请求数量，避免被封禁
- **缓存策略**: Redis缓存热点数据，减少重复请求
- **增量更新**: 仅更新变化的数据，提高效率

### 错误处理
- **重试机制**: 网络异常自动重试，指数退避
- **降级策略**: 主数据源失败时使用备用源
- **数据验证**: 多层验证确保数据完整性

### 合规性
- **访问频率**: 遵守robots.txt，合理控制请求频率
- **数据使用**: 遵循各数据源的使用条款
- **版权保护**: 官方图片等受版权保护的内容需要特殊处理

这个数据获取策略确保了系统能够稳定、高效地获取和维护原神游戏信息，为用户提供准确和及时的数据服务。