# proxy_backend.py
import asyncio
import aiohttp
import time
import json
import os
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import winsound
import logging
from dataclasses import dataclass
from enum import Enum
import aiofiles

# تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proxy_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ProxyBackend')

class ProxyStatus(Enum):
    ACTIVE = "Active"
    FAILED = "Failed"
    TIMEOUT = "Timeout"
    ERROR = "Error"

class AnonymityLevel(Enum):
    ELITE = "Elite"
    ANONYMOUS = "Anonymous"
    TRANSPARENT = "Transparent"
    UNKNOWN = "Unknown"

@dataclass
class ProxyResult:
    proxy: str
    ping: int
    http_time: int
    status: ProxyStatus
    country: str = "Unknown"
    country_code: str = "XX"
    anonymity: AnonymityLevel = AnonymityLevel.UNKNOWN
    last_checked: str = None
    isp: str = "Unknown"

    def to_dict(self):
        return {
            'proxy': self.proxy,
            'ping': self.ping,
            'http_time': self.http_time,
            'status': self.status.value,
            'country': self.country,
            'country_code': self.country_code,
            'anonymity': self.anonymity.value,
            'last_checked': self.last_checked,
            'isp': self.isp
        }

class ProxyBackend:
    def __init__(self):
        self.proxy_list: List[str] = []
        self.test_results: List[ProxyResult] = []
        self.best_proxy: Optional[str] = None
        self.is_testing: bool = False
        self.working_proxies_file: str = "working_proxies_live.txt"
        self.config_file: str = "config.json"
        
        # تنظیمات پیشرفته
        self.settings = {
            'max_workers': 50,
            'timeout': 8,
            'test_urls': [
                'http://www.google.com',
                'http://www.cloudflare.com',
                'http://www.github.com',
                'https://httpbin.org/ip'
            ],
            'enable_sound': True,
            'test_https': True
        }
        
        # لود تنظیمات
        self.load_settings()
        
        # ایجاد فایل working پروکسی‌ها اگر وجود ندارد
        self._ensure_working_proxies_file()
    
    def load_settings(self):
        """لود تنظیمات از فایل"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
                logger.info("Settings loaded from config file")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """ذخیره تنظیمات در فایل"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info("Settings saved to config file")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def _ensure_working_proxies_file(self):
        """ایجاد فایل working پروکسی‌ها"""
        if not os.path.exists(self.working_proxies_file):
            with open(self.working_proxies_file, 'w', encoding='utf-8') as f:
                f.write("# Working Proxies - Auto-generated\n")
            logger.info("Created working proxies file")

    def load_proxies_from_file(self, filename="proxies.txt"):
        """لود پروکسی‌ها از فایل با حذف duplicate و پشتیبانی از فرمت‌های مختلف"""
        try:
            if not os.path.exists(filename):
                return True, "No proxy file found. Please load a proxy file or add proxies manually."
            
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            loaded_proxies = []
            seen_proxies = set()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # پشتیبانی از فرمت‌های مختلف
                    proxy = self._parse_proxy_line(line)
                    if proxy and proxy not in seen_proxies:
                        loaded_proxies.append(proxy)
                        seen_proxies.add(proxy)
            
            self.proxy_list = loaded_proxies
            
            # لود پروکسی‌های working اگر وجود دارند
            self._load_working_proxies()
            
            logger.info(f"Loaded {len(self.proxy_list)} unique proxies from {filename}")
            return True, f"✅ {len(self.proxy_list)} unique proxies loaded"
            
        except Exception as e:
            logger.error(f"Error loading proxies: {e}")
            return False, f"❌ Error loading file: {str(e)}"
    
    def _parse_proxy_line(self, line: str) -> str:
        """پارس کردن خط پروکسی با پشتیبانی از فرمت‌های مختلف"""
        line = line.strip()
        
        # فرمت: user:pass@ip:port
        if '@' in line:
            parts = line.split('@')
            if len(parts) == 2 and ':' in parts[1]:
                return parts[1]  # فقط ip:port برمی‌گردانیم
        
        # فرمت: ip:port:user:pass
        if line.count(':') == 3:
            parts = line.split(':')
            return f"{parts[0]}:{parts[1]}"  # فقط ip:port برمی‌گردانیم
        
        # فرمت استاندارد: ip:port
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2 and parts[1].isdigit():
                return line
        
        return ""

    def _load_working_proxies(self):
        """لود پروکسی‌های working از فایل"""
        try:
            if os.path.exists(self.working_proxies_file):
                with open(self.working_proxies_file, 'r', encoding='utf-8') as f:
                    working_proxies = [line.strip() for line in f 
                                     if line.strip() and not line.startswith('#')]
                
                # اضافه کردن به لیست اصلی (بدون تکراری)
                for proxy in working_proxies:
                    parsed = self._parse_proxy_line(proxy)
                    if parsed and parsed not in self.proxy_list:
                        self.proxy_list.append(parsed)
                
                logger.info(f"Loaded {len(working_proxies)} working proxies from cache")
                
        except Exception as e:
            logger.error(f"Error loading working proxies: {e}")

    async def test_proxy_async(self, proxy: str, session: aiohttp.ClientSession) -> ProxyResult:
        """تست پروکسی به صورت ناهمزمان با پشتیبانی کامل"""
        start_time = time.time()
        
        try:
            ip, port = proxy.split(':')
            
            # تست اتصال TCP با asyncio (غیر بلاک‌کننده)
            try:
                tcp_start = time.time()
                conn = asyncio.open_connection(ip, int(port))
                reader, writer = await asyncio.wait_for(conn, timeout=5)
                writer.close()
                await writer.wait_closed()
                connect_time = int((time.time() - tcp_start) * 1000)
            except (asyncio.TimeoutError, ConnectionRefusedError, ConnectionResetError, OSError) as e:
                logger.debug(f"TCP connection failed for {proxy}: {e}")
                return ProxyResult(proxy, 9999, 9999, ProxyStatus.FAILED)
            
            # تست HTTP
            http_time, http_success = await self._test_http_proxy(proxy, session)
            
            if not http_success and self.settings['test_https']:
                # تست HTTPS اگر HTTP شکست خورد
                http_time, http_success = await self._test_https_proxy(proxy, session)
            
            if http_success:
                # تشخیص کشور و anonymity
                country, country_code, anonymity, isp = await self._detect_proxy_info(ip, session)
                
                # ذخیره سریع پروکسی سالم - فقط اگر http_time کمتر از 3000 باشد
                if http_time < 3000:
                    await self._save_working_proxy_immediately(proxy)
                
                return ProxyResult(
                    proxy=proxy,
                    ping=connect_time,
                    http_time=http_time,
                    status=ProxyStatus.ACTIVE,
                    country=country,
                    country_code=country_code,
                    anonymity=anonymity,
                    isp=isp,
                    last_checked=datetime.now().isoformat()
                )
            else:
                return ProxyResult(proxy, connect_time, 9999, ProxyStatus.FAILED)
            
        except Exception as e:
            logger.debug(f"Error testing proxy {proxy}: {e}")
            return ProxyResult(proxy, 9999, 9999, ProxyStatus.ERROR)    
    async def _test_http_proxy(self, proxy: str, session: aiohttp.ClientSession) -> tuple[int, bool]:
        """تست HTTP proxy"""
        proxies = f'http://{proxy}'
        
        for url in self.settings['test_urls']:
            if not url.startswith('http://'):
                continue
                
            try:
                http_start = time.time()
                async with session.get(
                    url, 
                    proxy=proxies,
                    timeout=aiohttp.ClientTimeout(total=self.settings['timeout']),
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                    ssl=False
                ) as response:
                    if response.status == 200:
                        return int((time.time() - http_start) * 1000), True
            except:
                continue
        
        return 9999, False

    async def _test_https_proxy(self, proxy: str, session: aiohttp.ClientSession) -> tuple[int, bool]:
        """تست HTTPS proxy"""
        proxies = f'http://{proxy}'
        
        for url in self.settings['test_urls']:
            if not url.startswith('https://'):
                continue
                
            try:
                http_start = time.time()
                async with session.get(
                    url, 
                    proxy=proxies,
                    timeout=aiohttp.ClientTimeout(total=self.settings['timeout']),
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                ) as response:
                    if response.status == 200:
                        return int((time.time() - http_start) * 1000), True
            except:
                continue
        
        return 9999, False

    async def _detect_proxy_info(self, ip: str, session: aiohttp.ClientSession) -> tuple[str, str, AnonymityLevel, str]:
        """تشخیص کشور، anonymity و ISP پروکسی"""
        country, country_code, isp = "Unknown", "XX", "Unknown"
        anonymity = AnonymityLevel.UNKNOWN
        
        try:
            # تشخیص کشور و ISP از ip-api.com
            async with session.get(
                f'http://ip-api.com/json/{ip}',
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        country = data.get('country', 'Unknown')
                        country_code = data.get('countryCode', 'XX')
                        isp = data.get('isp', 'Unknown')
            
            # تست anonymity از httpbin.org
            async with session.get(
                'http://httpbin.org/ip',
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    headers = dict(response.headers)
                    if 'via' in headers or 'x-forwarded-for' in headers:
                        anonymity = AnonymityLevel.TRANSPARENT
                    else:
                        anonymity = AnonymityLevel.ANONYMOUS
                        
        except:
            pass
        
        return country, country_code, anonymity, isp

    async def _save_working_proxy_immediately(self, proxy: str):
        """ذخیره فوری پروکسی سالم در فایل"""
        try:
            # استفاده از threading برای جلوگیری از مشکل event loop
            import threading
            
            def save_proxy():
                try:
                    # خواندن فایل فعلی
                    existing_proxies = set()
                    if os.path.exists(self.working_proxies_file):
                        with open(self.working_proxies_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    existing_proxies.add(line)
                    
                    # اضافه کردن پروکسی جدید
                    if proxy not in existing_proxies:
                        with open(self.working_proxies_file, 'a', encoding='utf-8') as f:
                            f.write(f"{proxy}\n")
                            
                except Exception as e:
                    logger.error(f"Error quick saving proxy: {e}")
            
            # اجرا در thread جداگانه
            thread = threading.Thread(target=save_proxy)
            thread.daemon = True
            thread.start()
            thread.join(timeout=2)  # تایم‌اوت برای جلوگیری از block شدن
            
        except Exception as e:
            logger.error(f"Error in quick save thread: {e}")
        
    async def run_full_test_async(self, progress_callback: Callable = None, result_callback: Callable = None):
        """اجرای تست کامل به صورت ناهمزمان"""
        if self.is_testing:
            return False, {"error": "Test already in progress"}
        
        if not self.proxy_list:
            return False, {"error": "No proxies loaded"}
        
        self.is_testing = True
        self.test_results = []
        self.best_proxy = None
        
        try:
            # ایجاد سمیفور برای محدود کردن concurrent connections
            semaphore = asyncio.Semaphore(self.settings['max_workers'])
            
            async def test_with_semaphore(proxy):
                async with semaphore:
                    if not self.is_testing:
                        return None
                    
                    result = await self.test_proxy_async(proxy, session)
                    
                    # فرستادن نتیجه به فرانت‌اند
                    if result_callback:
                        result_callback(result.to_dict())
                    
                    return result
            
            connector = aiohttp.TCPConnector(limit=self.settings['max_workers'], verify_ssl=False)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = []
                for proxy in self.proxy_list:
                    if not self.is_testing:
                        break
                    task = asyncio.create_task(test_with_semaphore(proxy))
                    tasks.append(task)
                
                completed = 0
                total = len(tasks)
                
                for future in asyncio.as_completed(tasks):
                    if not self.is_testing:
                        # لغو تسک‌های باقی‌مانده به درستی
                        for task in tasks:
                            if not task.done():
                                task.cancel()
                        try:
                            await asyncio.gather(*tasks, return_exceptions=True)
                        except:
                            pass
                        break
                    
                    try:
                        result = await future
                        if result:
                            self.test_results.append(result)
                            completed += 1
                            
                            # آپدیت بهترین پروکسی
                            if result.status == ProxyStatus.ACTIVE:
                                if not self.best_proxy:
                                    self.best_proxy = result.proxy
                                else:
                                    current_best = next((r for r in self.test_results if r.proxy == self.best_proxy), None)
                                    if current_best:
                                        if result.http_time < current_best.http_time:
                                            self.best_proxy = result.proxy
                                        elif result.http_time == current_best.http_time and result.ping < current_best.ping:
                                            self.best_proxy = result.proxy
                            
                            # فرستادن پیشرفت به فرانت‌اند
                            if progress_callback:
                                progress_callback(completed, total)
                                
                    except Exception as e:
                        logger.debug(f"Error in async test: {e}")
                        completed += 1
                        if progress_callback:
                            progress_callback(completed, total)
            
            return self._compile_final_stats()
            
        except Exception as e:
            logger.error(f"Async test failed: {e}")
            return False, {"error": str(e)}
        finally:
            self.is_testing = False
        
    def stop_testing(self):
        """توقف کامل تست"""
        self.is_testing = False
        logger.info("Test stopped by user")

    def _compile_final_stats(self) -> tuple[bool, dict]:
        """کامپایل آمار نهایی"""
        active_results = [r for r in self.test_results if r.status == ProxyStatus.ACTIVE]
        failed_results = [r for r in self.test_results if r.status != ProxyStatus.ACTIVE]
        
        active_pings = [r.ping for r in active_results]
        active_http_times = [r.http_time for r in active_results]
        
        best_ping = min(active_pings) if active_pings else 0
        avg_ping = sum(active_pings) // len(active_pings) if active_pings else 0
        best_http_time = min(active_http_times) if active_http_times else 0
        avg_http_time = sum(active_http_times) // len(active_http_times) if active_http_times else 0
        
        stats = {
            'total': len(self.proxy_list),
            'tested': len(self.test_results),
            'active': len(active_results),
            'failed': len(failed_results),
            'best_ping': best_ping,
            'avg_ping': avg_ping,
            'best_http_time': best_http_time,
            'avg_http_time': avg_http_time,
            'best_proxy': self.best_proxy,
            'success_rate': (len(active_results) / len(self.test_results) * 100) if self.test_results else 0
        }
        
        return True, stats

    def get_stats(self) -> dict:
        """گرفتن آمار نهایی"""
        if not self.test_results:
            return {}
        
        active_results = [r for r in self.test_results if r.status == ProxyStatus.ACTIVE]
        success_rate = (len(active_results) / len(self.test_results) * 100) if self.test_results else 0
        
        active_http_times = [r.http_time for r in active_results]
        best_http_time = min(active_http_times) if active_http_times else 0
        
        return {
            'total_proxies': len(self.proxy_list),
            'tested_proxies': len(self.test_results),
            'active_proxies': len(active_results),
            'success_rate': success_rate,
            'best_proxy': self.best_proxy,
            'best_ping': min([r.ping for r in active_results]) if active_results else 0,
            'best_http_time': best_http_time
        }

    def save_working_proxies(self, filename=None):
        """ذخیره پروکسی‌های سالم"""
        if not filename:
            filename = f"working_proxies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            working_proxies = [result.proxy for result in self.test_results 
                             if result.status == ProxyStatus.ACTIVE]
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Working Proxies - Exported {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                for proxy in working_proxies:
                    f.write(proxy + '\n')
            
            return True, f"✅ {len(working_proxies)} working proxies saved to {filename}"
        except Exception as e:
            return False, f"❌ Error saving file: {str(e)}"

    def set_windows_proxy(self, proxy: str) -> tuple[bool, str]:
        """تنظیم پروکسی در ویندوز"""
        if not proxy or ':' not in proxy:
            return False, "Invalid proxy format"
        
        try:
            ip, port = proxy.split(':')
            
            # بررسی اینکه پورت عدد معتبر باشد
            if not port.isdigit() or not (1 <= int(port) <= 65535):
                return False, "Invalid port number"
            
            # تنظیم از طریق netsh با دستور کامل
            cmd = f'netsh winhttp set proxy {ip}:{port}'
            logger.info(f"Executing command: {cmd}")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', timeout=15)
            
            logger.info(f"Command return code: {result.returncode}")
            logger.info(f"Command stdout: {result.stdout}")
            logger.info(f"Command stderr: {result.stderr}")
            
            if result.returncode == 0:
                # تأیید که پروکسی واقعاً تنظیم شده است
                verification_success, verification_msg = self.verify_proxy_setting(proxy)
                
                if self.settings['enable_sound']:
                    try:
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    except:
                        pass
                
                if verification_success:
                    logger.info(f"Proxy set and verified successfully: {proxy}")
                    return True, f"✅ Proxy set: {proxy}"
                else:
                    logger.warning(f"Proxy set but verification failed: {verification_msg}")
                    return True, f"⚠️ Proxy set (verification pending): {proxy}"
            else:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                if not error_msg:
                    error_msg = f"Command failed with code {result.returncode}"
                    
                logger.error(f"Failed to set proxy: {error_msg}")
                return False, f"❌ Failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            logger.error("Proxy setting timeout")
            return False, "❌ Timeout setting proxy"
        except Exception as e:
            logger.error(f"Error setting proxy: {e}")
            return False, f"❌ Error: {str(e)}"

    def verify_proxy_setting(self, expected_proxy: str) -> tuple[bool, str]:
        """تأیید اینکه پروکسی واقعاً تنظیم شده است"""
        try:
            cmd = 'netsh winhttp show proxy'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                if 'direct access' in output or 'none' in output:
                    return False, "No proxy set (direct access)"
                
                # استخراج پروکسی تنظیم شده از خروجی
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'proxy server' in line.lower():
                        set_proxy = line.split(':')[1].strip() if ':' in line else line.strip()
                        if expected_proxy in set_proxy:
                            return True, f"Verified: {set_proxy}"
                        else:
                            return False, f"Proxy mismatch. Expected: {expected_proxy}, Got: {set_proxy}"
                
                return False, "Proxy server not found in output"
            else:
                return False, f"Verification command failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Verification error: {str(e)}"
    
    def get_sorted_results(self, sort_by='http_time') -> List[dict]:
        """گرفتن نتایج سورت شده"""
        if not self.test_results:
            return []
        
        if sort_by == 'ping':
            sorted_results = sorted(self.test_results, key=lambda x: x.ping)
        elif sort_by == 'http_time':
            sorted_results = sorted(self.test_results, key=lambda x: x.http_time)
        elif sort_by == 'status':
            sorted_results = sorted(self.test_results, key=lambda x: x.status.value)
        elif sort_by == 'proxy':
            sorted_results = sorted(self.test_results, key=lambda x: x.proxy)
        elif sort_by == 'country':
            sorted_results = sorted(self.test_results, key=lambda x: x.country)
        else:
            sorted_results = self.test_results
        
        return [r.to_dict() for r in sorted_results]

    def get_filtered_results(self, filters: dict) -> List[dict]:
        """گرفتن نتایج فیلتر شده"""
        if not self.test_results:
            return []
        
        filtered = self.test_results
        
        if filters.get('active_only'):
            filtered = [r for r in filtered if r.status == ProxyStatus.ACTIVE]
        
        if filters.get('max_ping'):
            filtered = [r for r in filtered if r.ping <= filters['max_ping']]
        
        if filters.get('max_http_time'):
            filtered = [r for r in filtered if r.http_time <= filters['max_http_time']]
        
        if filters.get('country'):
            filtered = [r for r in filtered if r.country.lower() == filters['country'].lower()]
        
        return [r.to_dict() for r in filtered]

    def export_results_json(self, filename: str = None) -> tuple[bool, str]:
        """اکسپورت نتایج به JSON"""
        if not filename:
            filename = f"proxy_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'total_proxies': len(self.proxy_list),
                'tested_proxies': len(self.test_results),
                'test_results': [r.to_dict() for r in self.test_results],
                'best_proxy': self.best_proxy,
                'stats': self.get_stats()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results exported to {filename}")
            return True, f"✅ Exported to {filename}"
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False, f"❌ Export failed: {str(e)}"

    def add_proxy_manual(self, proxy: str) -> tuple[bool, str]:
        """اضافه کردن دستی پروکسی"""
        try:
            parsed = self._parse_proxy_line(proxy)
            if not parsed:
                return False, "Invalid format. Use IP:PORT or host:PORT"
            
            if parsed in self.proxy_list:
                return False, "Proxy already exists"
            
            self.proxy_list.append(parsed)
            
            logger.info(f"Proxy added manually: {parsed}")
            return True, f"✅ Added: {parsed}"
            
        except Exception as e:
            logger.error(f"Error adding proxy: {e}")
            return False, f"❌ Error: {str(e)}"

    def get_connection_status(self) -> tuple[bool, str]:
        """بررسی وضعیت اتصال"""
        try:
            import requests
            response = requests.get('http://www.google.com', timeout=5)
            
            # بررسی اگر پروکسی تنظیم شده
            proxy_status = self._check_current_proxy()
            if proxy_status and proxy_status != "No Proxy":
                return True, f"🌐 Connected ({proxy_status})"
            else:
                return True, "🌐 Connected (No Proxy)"
                
        except requests.exceptions.RequestException:
            return False, "❌ No Internet Connection"
        except Exception as e:
            logger.error(f"Connection check error: {e}")
            return False, "❌ Connection Error"
    
    def _check_current_proxy(self) -> str:
        """بررسی پروکسی فعلی سیستم"""
        try:
            result = subprocess.run('netsh winhttp show proxy', shell=True, 
                                  capture_output=True, text=True, encoding='utf-8')
            if 'Direct access' in result.stdout:
                return "No Proxy"
            elif 'Proxy Server' in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Proxy Server' in line:
                        return line.split(':')[1].strip()
            return "Unknown"
        except:
            return "Unknown"

    def auto_set_best_proxy(self) -> tuple[bool, str]:
        """تنظیم اتوماتیک بهترین پروکسی"""
        if not self.best_proxy:
            return False, "No best proxy available"
        return self.set_windows_proxy(self.best_proxy)

    def clear_all(self):
        """پاک کردن همه داده‌ها"""
        self.proxy_list.clear()
        self.test_results.clear()
        self.best_proxy = None
        self.is_testing = False
        logger.info("All data cleared")

    def update_settings(self, new_settings: dict):
        """آپدیت تنظیمات"""
        self.settings.update(new_settings)
        self.save_settings()
        logger.info("Settings updated")

    def test_single_proxy(self, proxy: str) -> ProxyResult:
        """تست یک پروکسی خاص"""
        async def run_single_test():
            connector = aiohttp.TCPConnector(verify_ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                return await self.test_proxy_async(proxy, session)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(run_single_test())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error testing single proxy: {e}")
            return ProxyResult(proxy, 9999, 9999, ProxyStatus.ERROR)

    def import_from_clipboard(self) -> tuple[bool, str]:
        """ایمپورت پروکسی‌ها از کلیپ‌بورد"""
        try:
            import tkinter as tk
            clipboard = tk.Tk().clipboard_get()
            lines = clipboard.split('\n')
            
            imported_count = 0
            for line in lines:
                proxy = self._parse_proxy_line(line.strip())
                if proxy and proxy not in self.proxy_list:
                    self.proxy_list.append(proxy)
                    imported_count += 1
            
            if imported_count > 0:
                return True, f"✅ {imported_count} proxies imported from clipboard"
            else:
                return False, "❌ No valid proxies found in clipboard"
                
        except Exception as e:
            return False, f"❌ Error importing from clipboard: {str(e)}"

    def get_smart_best_proxy(self) -> Optional[str]:
        """پیدا کردن بهترین پروکسی از بین نتایج تست و فایل working"""
        best_proxy = None
        best_http_time = float('inf')
        best_ping = float('inf')
        
        # بررسی پروکسی‌های تست شده
        for result in self.test_results:
            if result.status == ProxyStatus.ACTIVE:
                if result.http_time < best_http_time:
                    best_http_time = result.http_time
                    best_ping = result.ping
                    best_proxy = result.proxy
                elif result.http_time == best_http_time and result.ping < best_ping:
                    best_ping = result.ping
                    best_proxy = result.proxy
        
        # اگر پروکسی فعالی در نتایج تست نبود، فایل working را بررسی کن
        if not best_proxy and os.path.exists(self.working_proxies_file):
            try:
                with open(self.working_proxies_file, 'r', encoding='utf-8') as f:
                    working_proxies = [line.strip() for line in f 
                                     if line.strip() and not line.startswith('#')]
                
                # اولین پروکسی از فایل working را انتخاب کن
                if working_proxies:
                    best_proxy = working_proxies[0]
            except Exception as e:
                logger.error(f"Error reading working proxies file: {e}")
        
        return best_proxy

# تست واحد
if __name__ == "__main__":
    async def test_backend():
        backend = ProxyBackend()
        
        # تست لود پروکسی‌ها
        success, message = backend.load_proxies_from_file()
        print(f"Load: {success} - {message}")
        
        # تست وضعیت اتصال
        connected, status = backend.get_connection_status()
        print(f"Connection: {connected} - {status}")
        
        print("Backend test completed successfully")
    
    asyncio.run(test_backend())