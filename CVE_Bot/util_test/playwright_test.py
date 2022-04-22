import asyncio

from playwright.async_api import async_playwright


async def test():
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto("https://cxsecurity.com/wlb/1")
        await page.locator('#glowna > center > div > div:nth-child(4) > ul > li:nth-child(13) > a').click()
        total = int(page.url.strip('https://cxsecurity.com/wlb/'))
        await browser.close()
        return total


if __name__ == "__main__":
    print(asyncio.run(test()))
    print(1)
