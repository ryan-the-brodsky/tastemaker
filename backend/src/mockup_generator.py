"""
Mockup PNG Generator Service.
Uses Playwright to capture mockup pages as PNG images.
"""
import os
import tempfile
import asyncio
from typing import Optional
from pathlib import Path

# Try to import playwright, but don't fail if not available
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Mockup generation will use fallback mode.")


MOCKUP_TYPES = ['landing', 'dashboard', 'form', 'settings']
MOCKUP_WIDTH = 1200
MOCKUP_HEIGHT = 800


async def generate_mockup_pngs(
    session_id: int,
    frontend_url: str = "http://localhost:5173",
    output_dir: Optional[str] = None
) -> dict:
    """
    Generate PNG mockups for a session using Playwright.

    Args:
        session_id: The session ID to generate mockups for
        frontend_url: Base URL of the frontend server
        output_dir: Directory to save PNGs (defaults to temp dir)

    Returns:
        dict with success status and paths to generated PNGs
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "success": False,
            "error": "Playwright not installed. Run: pip install playwright && playwright install chromium",
            "mockups": {}
        }

    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), f"tastemaker-mockups-{session_id}")

    os.makedirs(output_dir, exist_ok=True)

    mockups = {}
    errors = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Set viewport to match mockup dimensions
            await page.set_viewport_size({"width": MOCKUP_WIDTH, "height": MOCKUP_HEIGHT})

            for mockup_type in MOCKUP_TYPES:
                try:
                    url = f"{frontend_url}/mockup-render/{session_id}/{mockup_type}"

                    # Navigate and wait for content to load
                    await page.goto(url, wait_until="networkidle")

                    # Wait a bit for fonts and styles to fully load
                    await page.wait_for_timeout(1000)

                    # Wait for the mockup container to be ready
                    await page.wait_for_selector("#mockup-container", timeout=5000)

                    # Take screenshot
                    output_path = os.path.join(output_dir, f"{mockup_type}.png")
                    await page.screenshot(
                        path=output_path,
                        full_page=False,
                        clip={"x": 0, "y": 0, "width": MOCKUP_WIDTH, "height": MOCKUP_HEIGHT}
                    )

                    mockups[mockup_type] = output_path

                except Exception as e:
                    errors.append(f"{mockup_type}: {str(e)}")

            await browser.close()

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "mockups": mockups
        }

    return {
        "success": len(errors) == 0,
        "mockups": mockups,
        "errors": errors if errors else None,
        "output_dir": output_dir
    }


def generate_mockup_pngs_sync(
    session_id: int,
    frontend_url: str = "http://localhost:5173",
    output_dir: Optional[str] = None
) -> dict:
    """
    Synchronous wrapper for generate_mockup_pngs.
    """
    return asyncio.run(generate_mockup_pngs(session_id, frontend_url, output_dir))


def get_mockup_paths(session_id: int) -> dict:
    """
    Get paths to existing mockup PNGs for a session.
    Returns dict mapping mockup type to file path.
    """
    output_dir = os.path.join(tempfile.gettempdir(), f"tastemaker-mockups-{session_id}")

    if not os.path.exists(output_dir):
        return {}

    mockups = {}
    for mockup_type in MOCKUP_TYPES:
        path = os.path.join(output_dir, f"{mockup_type}.png")
        if os.path.exists(path):
            mockups[mockup_type] = path

    return mockups


def mockups_exist(session_id: int) -> bool:
    """
    Check if all mockup PNGs exist for a session.
    """
    paths = get_mockup_paths(session_id)
    return len(paths) == len(MOCKUP_TYPES)
