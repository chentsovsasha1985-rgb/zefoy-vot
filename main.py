"""
Zefoy-CLI Automation - Docker Compatible Entry Point
Repository: https://github.com
"""
import argparse
import asyncio
import sys
import os
import warnings

# Жесткое исправление путей поиска модулей для Docker на Render
sys.path.insert(0, "/app")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from browser.automation import ZefoyAutomation, SERVICES, create_automation
from utils.timer import wait_with_progress
from utils.health_check import check_site_status
from utils.colors import success, error, warning, info

warnings.filterwarnings("ignore", category=ResourceWarning)

async def clear_cookies_standalone() -> None:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://zefoy.com")
        await context.clear_cookies()
        await browser.close()
        print("  Cookies cleared successfully!")

async def main() -> None:
    parser = argparse.ArgumentParser(description="Zefoy CLI Automation Tool")
    parser.add_argument("url", nargs="?", help="TikTok video URL")
    parser.add_argument("--service", choices=list(SERVICES.keys()), help="Automation service to use")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--auto-captcha", action="store_true", default=True, help="Enable automatic CAPTCHA solving")
    parser.add_argument("--no-wait", action="store_true", default=False, help="Disable automatic waiting on rate limits")
    parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose logging")
    parser.add_argument("--proxy", help="Proxy server URL")
    parser.add_argument("--count", type=int, default=100, help="Target number of successful interactions")
    parser.add_argument("--clear-cookies", action="store_true", help="Clear zefoy.com cookies before starting")
    
    args = parser.parse_args()
    
    if args.clear_cookies:
        print("Clearing standalone cookies...")
        await clear_cookies_standalone()
        if not args.url: return

    # Ваша ссылка автоматически подставляется здесь
    url = "https://tiktok.com"
    print(f"Target URL set to: {url}")

    print("Checking zefoy.com availability...")
    is_up, message = check_site_status()
    if not is_up:
        print(f"Site check failed: {message}")
        return

    # Автоматически выбираем просмотры (views) для накрутки
    service = args.service or "views"
    print(f"Selected service: {service}")

    automation = create_automation(
        headless=True, auto_captcha=True,
        verbose=args.verbose, proxy_url=args.proxy
    )
    
    successful_sends = 0
    
    try:
        print("Initializing Browser & Navigating...")
        await automation.init_browser()
        await automation.navigate_to_zefoy()
        
        if not await automation.solve_captcha_loop():
            print("Failed to solve CAPTCHA. Exiting...")
            return
            
        if not await automation.select_service(service):
            await automation.detect_available_services()
            if not automation._available_services.get(service):
                print(f"Service \"{service}\" is not available!")                                          
                return
            if not await automation.select_service(service):
                print(f"Failed to select {service} service. Exiting...")
                return

        print("Starting Interaction Loop...")
        while successful_sends < args.count:
            print(f"\nProgress: {successful_sends}/{args.count}")
            
            if not await automation.submit_url(url):
                print("URL submission failed. Retrying in 5 seconds...")
                await asyncio.sleep(5)
                continue

            has_timer, seconds = await automation.check_timer()
            if has_timer:
                if args.no_wait:
                    print("Rate limit active. --no-wait active, exiting...")
                    break
                print(f"Rate limit detected. Waiting {seconds}s...")
                await wait_with_progress(seconds)
                continue

            print("Sending interaction request...")
            send_success, msg = await automation.trigger_action()

            if send_success:
                successful_sends += 1
                print(f"Successfully sent! Zefoy: {msg}")
                if successful_sends < args.count:
                    await asyncio.sleep(10)
            else:
                print(f"Send failed: {msg}. Retrying in 5s...")
                await asyncio.sleep(5)

    except KeyboardInterrupt:
        print("\nAutomation interrupted by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    finally:
        print("Closing browser and cleaning up...")
        await automation.close()
        print(f"Session finished. Completed {successful_sends}/{args.count} sends.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
