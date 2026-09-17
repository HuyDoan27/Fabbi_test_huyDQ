import { test, expect } from "@playwright/test";

test("register, login, create todo, toggle and logout", async ({ page }) => {
    const email = `e2e-${Date.now()}@test.com`;
    const password = "Password123!";

    // Register
    await page.goto("/register");

    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password", { exact: true }).fill(password);
    await page.getByLabel("Confirm Password", { exact: true }).fill(password);

    await page.getByRole("button", { name: "Create Account" }).click();

    // Login
    // Login
    await expect(page).toHaveURL(/\/$/);
    await page.goto("/login");

    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill(password);

    await page.getByRole("button", { name: "Sign In" }).click();

    // Todo page
    await expect(page).toHaveURL(/\/$/);
    // Open create todo form
    await page.getByRole("button", { name: "Add Todo" }).click();

    // Create todo
    const todoTitle = `E2E Todo ${Date.now()}`;

    await page.getByPlaceholder("What needs to be done?").fill(todoTitle);
    await page.getByRole("button", { name: "Create", exact: true }).click();

    // Verify todo appears
    const todo = page.getByText(todoTitle, { exact: true });
    await expect(todo).toBeVisible();

    // Toggle completed
    // Toggle completed
    const checkbox = page.getByRole("checkbox", { name: todoTitle });

    await checkbox.click();

    await expect(checkbox).toBeChecked();

    // Verify completed state
    await expect(checkbox).toBeChecked();

    // Logout
    await page.getByRole("button", { name: "Logout" }).click();

    await expect(page).toHaveURL(/\/login/);
});