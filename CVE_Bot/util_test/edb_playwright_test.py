import asyncio

from playwright.async_api import async_playwright


async def test():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.exploit-db.com/search")
        table = page.locator('#exploits-table > tbody:nth-child(2) > tr')
        await browser.close()


if __name__ == "__main__":
    print(asyncio.run(test()))
