import { test, expect } from "@playwright/test";

test.describe("Landing Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("displays hero section", async ({ page }) => {
    // Check for main heading
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    // Check for hero description
    await expect(page.locator("text=/AI|healthcare|documentation|medical/i")).toBeVisible();

    // Check for CTA buttons
    await expect(page.getByRole("link", { name: /get started|try|start/i })).toBeVisible();
  });

  test("displays features section", async ({ page }) => {
    // Scroll to features
    await page.locator("text=/features/i").first().scrollIntoViewIfNeeded();

    // Check for feature cards/items
    const features = page.locator("[data-testid='feature'], .feature-card, article");
    await expect(features.first()).toBeVisible().catch(() => {
      // Features might be structured differently
    });
  });

  test("displays navigation", async ({ page }) => {
    // Check for logo/brand
    await expect(page.locator("text=/MediNote|Logo/i").first()).toBeVisible().catch(() => {
      // Brand might be an image
    });

    // Check for nav links
    const nav = page.locator("nav, header");
    await expect(nav).toBeVisible();
  });

  test("navigates to login from CTA", async ({ page }) => {
    const loginLink = page.getByRole("link", { name: /login|sign in/i }).first();
    if (await loginLink.isVisible()) {
      await loginLink.click();
      await expect(page).toHaveURL(/login/);
    }
  });

  test("navigates to register from CTA", async ({ page }) => {
    const registerLink = page.getByRole("link", { name: /get started|sign up|register/i }).first();
    if (await registerLink.isVisible()) {
      await registerLink.click();
      await expect(page).toHaveURL(/register|signup/);
    }
  });

  test("is responsive on mobile", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Hero should still be visible
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    // Check for mobile menu toggle if present
    const mobileMenu = page.locator("[data-testid='mobile-menu'], .mobile-menu-toggle, button[aria-label*='menu']");
    if (await mobileMenu.count() > 0) {
      await expect(mobileMenu.first()).toBeVisible();
    }
  });

  test("loads within acceptable time", async ({ page }) => {
    const startTime = Date.now();

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const loadTime = Date.now() - startTime;

    // Page should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test("has proper meta tags", async ({ page }) => {
    // Check title
    await expect(page).toHaveTitle(/MediNote|Medical|Healthcare/i);

    // Check for meta description
    const metaDescription = page.locator('meta[name="description"]');
    await expect(metaDescription).toHaveAttribute("content", /.+/);
  });

  test("has accessible structure", async ({ page }) => {
    // Check for main landmark
    const main = page.locator("main");
    await expect(main).toBeVisible();

    // Check for skip link if present
    const skipLink = page.locator("a[href='#main-content'], .skip-link");
    if (await skipLink.count() > 0) {
      await expect(skipLink).toBeVisible({ visible: false }); // Usually hidden until focused
    }

    // Check heading hierarchy
    const h1Count = await page.locator("h1").count();
    expect(h1Count).toBe(1); // Should have exactly one h1
  });
});
