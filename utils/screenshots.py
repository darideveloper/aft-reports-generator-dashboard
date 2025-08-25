from playwright.sync_api import sync_playwright


def render_image_from_url(
    url: str, output_path: str, width: int = 1000, height: int = 1000
):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(2000)  # wait for JS
        page.screenshot(path=output_path, full_page=True)
        browser.close()
