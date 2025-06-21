import asyncio
import base64
from io import BytesIO
from pathlib import Path
from typing import Optional
from PIL import Image
from playwright.async_api import async_playwright, Browser, Page
from config import Config

class ScreenshotService:
    """Service for capturing high-quality website screenshots"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.config = Config()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()
    
    async def capture_website(
        self, 
        url: str, 
        output_path: Optional[str] = None,
        full_page: bool = True,
        wait_for_load: bool = True
    ) -> str:
        """
        Capture a screenshot of a website
        
        Args:
            url: The website URL to capture
            output_path: Optional path to save the screenshot
            full_page: Whether to capture the full page or just viewport
            wait_for_load: Whether to wait for network idle
            
        Returns:
            Base64 encoded image string
        """
        if not self.browser:
            raise RuntimeError("ScreenshotService not initialized. Use as async context manager.")
        
        page = await self.browser.new_page(
            viewport={
                'width': self.config.SCREENSHOT_WIDTH,
                'height': self.config.SCREENSHOT_HEIGHT
            }
        )
        
        try:
            # Navigate to the URL
            await page.goto(url, timeout=self.config.SCREENSHOT_TIMEOUT)
            
            if wait_for_load:
                # Wait for network to be idle and for any dynamic content
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)  # Additional wait for dynamic content
            
            # Take screenshot
            screenshot_bytes = await page.screenshot(
                full_page=full_page,
                type='png'
            )
            
            # Save to file if path provided
            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(screenshot_bytes)
            
            # Convert to base64 for API
            base64_image = base64.b64encode(screenshot_bytes).decode('utf-8')
            return base64_image
            
        except Exception as e:
            raise Exception(f"Failed to capture screenshot: {str(e)}")
        
        finally:
            await page.close()
    
    async def capture_with_mobile_view(self, url: str) -> tuple[str, str]:
        """
        Capture both desktop and mobile views of a website
        
        Returns:
            Tuple of (desktop_base64, mobile_base64)
        """
        if not self.browser:
            raise RuntimeError("ScreenshotService not initialized.")
        
        # Desktop screenshot
        desktop_screenshot = await self.capture_website(url)
        
        # Mobile screenshot
        mobile_page = await self.browser.new_page(
            viewport={'width': 375, 'height': 812}  # iPhone X dimensions
        )
        
        try:
            await mobile_page.goto(url, timeout=self.config.SCREENSHOT_TIMEOUT)
            await mobile_page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            mobile_screenshot_bytes = await mobile_page.screenshot(
                full_page=True,
                type='png'
            )
            mobile_base64 = base64.b64encode(mobile_screenshot_bytes).decode('utf-8')
            
            return desktop_screenshot, mobile_base64
            
        finally:
            await mobile_page.close()
    
    @staticmethod
    def optimize_image(base64_image: str, max_size: int = 20 * 1024 * 1024) -> str:
        """
        Optimize image size for API limits
        
        Args:
            base64_image: Base64 encoded image
            max_size: Maximum size in bytes (default 20MB for GPT-4 Vision)
            
        Returns:
            Optimized base64 image
        """
        # Decode base64 image
        image_data = base64.b64decode(base64_image)
        
        # Check if optimization is needed
        if len(image_data) <= max_size:
            return base64_image
        
        # Open image with PIL
        image = Image.open(BytesIO(image_data))
        
        # Calculate compression ratio
        compression_ratio = max_size / len(image_data)
        new_quality = max(10, int(95 * compression_ratio))
        
        # Compress image
        output_buffer = BytesIO()
        image.save(output_buffer, format='PNG', optimize=True, quality=new_quality)
        
        # If still too large, resize image
        if len(output_buffer.getvalue()) > max_size:
            # Resize image while maintaining aspect ratio
            resize_ratio = (max_size / len(output_buffer.getvalue())) ** 0.5
            new_width = int(image.width * resize_ratio)
            new_height = int(image.height * resize_ratio)
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            output_buffer = BytesIO()
            resized_image.save(output_buffer, format='PNG', optimize=True)
        
        # Return optimized base64 image
        return base64.b64encode(output_buffer.getvalue()).decode('utf-8') 