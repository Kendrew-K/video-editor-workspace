import os
import asyncio
from playwright.async_api import async_playwright

URL = "https://asiatimes.com/2026/06/rupiahs-plunge-pushes-indonesias-manufacturers-to-the-edge/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "article_screenshot.png")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)

        # Find the article headline and scroll it to the top of the viewport
        for sel in ["h1", ".entry-title", ".post-title", "article h1"]:
            el = page.locator(sel).first
            if await el.count() > 0:
                await el.scroll_into_view_if_needed()
                # Scroll back up 20px so headline isn't clipped at very top
                await page.evaluate("window.scrollBy(0, -20)")
                break

        await page.wait_for_timeout(500)
        # Full 1280x900 clip from current scroll position — captures headline +
        # featured image + first paragraphs of the article
        await page.screenshot(
            path=OUT,
            clip={"x": 0, "y": 0, "width": 1280, "height": 900},
        )
        print(f"Saved article screenshot: {OUT}")
        await browser.close()

asyncio.run(main())
