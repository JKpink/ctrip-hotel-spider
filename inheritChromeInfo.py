from playwright.sync_api import sync_playwright

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://hotels.ctrip.com")

        print("👉 请手动完成登录，然后回车")
        input()

        context.storage_state(path="ctrip_state.json")