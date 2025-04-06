from playwright.async_api import async_playwright


async def check_status(uci, password):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://ircc-tracker-suivi.apps.cic.gc.ca/en/login")

        # Step 1: Login
        await page.fill('input[name="uci"]', uci)
        await page.fill('input[name="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")

        # Step 2: Click 'View application history'
        await page.wait_for_selector(
            '[data-cy-button-id="app-details-btn"]', timeout=10000
        )
        await page.click('[data-cy-button-id="app-details-btn"]')
        await page.wait_for_load_state("networkidle")

        # Step 3: Find chip text under "Background verification"
        try:
            # Don't call .first() — it's a property
            heading = page.locator("h3:has-text('Background verification')").first

            # Go up to the nearest <summary> or its container
            container = heading.locator("xpath=ancestor::summary[1]")

            # Look for the chip text inside that container
            chip_text_locator = container.locator(".chip-text")
            await chip_text_locator.wait_for(timeout=5000)  # wait up to 5s

            chip_text = await chip_text_locator.inner_text()
            result = f"Background verification status: {chip_text}"
        except Exception as e:
            print(e)
            result = f"Could not retrieve background verification status. Error: {e}"

        # Step 4: Extract most recent history update
        try:
            # Locate the first activity item
            latest_activity = page.locator("#history-timeline .activity").first

            # Get the date and activity title
            date_text = await latest_activity.locator(".date").inner_text()
            activity_text = await latest_activity.locator(
                ".activity-title"
            ).inner_text()

            history_status = (
                f"Most recent update: {activity_text.strip()} on {date_text.strip()}"
            )
        except Exception as e:
            history_status = f"Could not retrieve history timeline. Error: {e}"

        await browser.close()
        return f"{result}\n\n{history_status}"
