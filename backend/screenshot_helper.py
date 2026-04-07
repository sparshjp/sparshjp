"""Safe Playwright screenshot helper — called as a subprocess with arguments, not string interpolation."""
import sys
import asyncio
from playwright.async_api import async_playwright


async def take_screenshot(url: str, output_path: str, full_page: bool, wait_ms: int):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        await page.goto(url, wait_until='networkidle', timeout=15000)
        await page.wait_for_timeout(wait_ms)
        await page.screenshot(path=output_path, full_page=full_page)
        await browser.close()
        print('OK')


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: screenshot_helper.py <url> <output_path> <full_page> <wait_ms>", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]
    output_path = sys.argv[2]
    full_page = sys.argv[3].lower() == 'true'
    wait_ms = int(sys.argv[4])
    asyncio.run(take_screenshot(url, output_path, full_page, wait_ms))
