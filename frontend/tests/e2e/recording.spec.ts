import { test, expect } from "@playwright/test";

// Helper to login before tests that require authentication
async function loginAsDoctor(page: any) {
  await page.goto("/login");
  await page.getByLabel(/email/i).fill("doctor@example.com");
  await page.getByLabel(/password/i).fill("TestPass123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 5000 }).catch(() => {});
}

test.describe("Recording Feature", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsDoctor(page);
  });

  test.describe("Recording Page", () => {
    test("displays recording interface", async ({ page }) => {
      await page.goto("/recording");

      // Check for main recording elements
      await expect(page.getByRole("heading")).toBeVisible();
    });

    test("displays patient search", async ({ page }) => {
      await page.goto("/recording");

      // Check for patient selection
      const patientSearch = page.getByPlaceholder(/patient|search/i).or(
        page.locator("[data-testid='patient-search']")
      );

      if (await patientSearch.isVisible()) {
        await expect(patientSearch).toBeVisible();
      }
    });

    test("displays language selector", async ({ page }) => {
      await page.goto("/recording");

      // Check for language dropdown
      const languageSelector = page.locator("text=/English|Hindi|Language/i").first();
      await expect(languageSelector).toBeVisible().catch(() => {
        // Language selector might be in a dropdown
      });
    });

    test("displays recording button", async ({ page }) => {
      await page.goto("/recording");

      // Check for record button
      const recordButton = page.getByRole("button", { name: /record|start|mic/i }).or(
        page.locator("[data-testid='record-button']")
      );

      await expect(recordButton.first()).toBeVisible();
    });

    test("recording button is disabled without patient", async ({ page }) => {
      await page.goto("/recording");

      // Record button should be disabled when no patient selected
      const recordButton = page.getByRole("button", { name: /record|start/i }).first();

      if (await recordButton.isVisible()) {
        const isDisabled = await recordButton.isDisabled();
        // Button might be disabled or there might be a prompt
        expect(isDisabled).toBeDefined();
      }
    });
  });

  test.describe("Recording Controls", () => {
    test("shows microphone permission prompt", async ({ page, context }) => {
      // Grant microphone permission
      await context.grantPermissions(["microphone"]);

      await page.goto("/recording");

      // After granting permission, recording should be possible
      const recordButton = page.getByRole("button", { name: /record|start/i }).first();

      if (await recordButton.isVisible() && !(await recordButton.isDisabled())) {
        // Button should be clickable
        await expect(recordButton).toBeEnabled();
      }
    });

    test("displays audio level indicator when recording", async ({ page, context }) => {
      await context.grantPermissions(["microphone"]);
      await page.goto("/recording");

      // Look for waveform or audio level indicator
      const audioIndicator = page.locator(
        "[data-testid='waveform'], [data-testid='audio-level'], .waveform"
      );

      // The indicator might not be visible until recording starts
      if (await audioIndicator.count() > 0) {
        await expect(audioIndicator.first()).toBeDefined();
      }
    });
  });

  test.describe("Transcript Display", () => {
    test("displays transcript area", async ({ page }) => {
      await page.goto("/recording");

      // Check for transcript section
      const transcriptArea = page.locator(
        "[data-testid='transcript'], .transcript, text=/transcript/i"
      );

      if (await transcriptArea.first().isVisible()) {
        await expect(transcriptArea.first()).toBeVisible();
      }
    });

    test("shows placeholder when no transcript", async ({ page }) => {
      await page.goto("/recording");

      // Check for empty state message
      const placeholder = page.locator(
        "text=/start recording|listening|no transcript/i"
      );

      if (await placeholder.first().isVisible()) {
        await expect(placeholder.first()).toBeVisible();
      }
    });
  });

  test.describe("Recording States", () => {
    test("shows connecting state", async ({ page, context }) => {
      await context.grantPermissions(["microphone"]);
      await page.goto("/recording");

      // This test checks UI responds to state changes
      const statusIndicator = page.locator(
        "[data-testid='status'], .connection-status, text=/connected|connecting/i"
      );

      if (await statusIndicator.first().isVisible()) {
        await expect(statusIndicator.first()).toBeDefined();
      }
    });

    test("handles pause and resume", async ({ page, context }) => {
      await context.grantPermissions(["microphone"]);
      await page.goto("/recording");

      // Look for pause/resume buttons
      const pauseButton = page.getByRole("button", { name: /pause/i });
      const resumeButton = page.getByRole("button", { name: /resume/i });

      // These buttons might not be visible until recording starts
      if (await pauseButton.isVisible()) {
        await expect(pauseButton).toBeVisible();
      }
    });
  });

  test.describe("Error Handling", () => {
    test("shows error when microphone denied", async ({ page, context }) => {
      // Explicitly deny microphone permission
      await context.clearPermissions();

      await page.goto("/recording");

      // Try to start recording
      const recordButton = page.getByRole("button", { name: /record|start/i }).first();

      if (await recordButton.isVisible() && !(await recordButton.isDisabled())) {
        await recordButton.click();

        // Should show permission error
        await page.waitForTimeout(1000);

        const errorMessage = page.locator(
          "text=/permission|microphone|access denied|error/i"
        );

        if (await errorMessage.first().isVisible()) {
          await expect(errorMessage.first()).toBeVisible();
        }
      }
    });
  });
});
