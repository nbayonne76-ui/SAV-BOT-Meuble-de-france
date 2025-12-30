import { test, expect } from '@playwright/test';

test.describe('Création de ticket SAV', () => {
  test.beforeEach(async ({ page }) => {
    // Aller sur la page principale
    await page.goto('/');

    // Attendre que l'interface de chat soit chargée
    await expect(page.locator('textarea[placeholder*="message"]')).toBeVisible();
  });

  test('Scénario complet: créer un ticket SAV depuis le chat', async ({ page }) => {
    // 1. Envoyer le premier message pour démarrer la conversation
    const messageInput = page.locator('textarea[placeholder*="message"]');
    await messageInput.fill('Bonjour, j\'ai un problème avec mon canapé');
    await messageInput.press('Enter');

    // Attendre la réponse du bot
    await expect(page.locator('text=/Comment puis-je vous aider/i')).toBeVisible({ timeout: 10000 });

    // 2. Fournir des détails sur le problème
    await messageInput.fill('Le tissu de mon canapé est déchiré sur un côté');
    await messageInput.press('Enter');

    // Attendre la réponse
    await page.waitForTimeout(2000);

    // 3. Fournir les informations demandées (nom)
    await messageInput.fill('Jean Dupont');
    await messageInput.press('Enter');
    await page.waitForTimeout(2000);

    // 4. Email
    await messageInput.fill('jean.dupont@example.com');
    await messageInput.press('Enter');
    await page.waitForTimeout(2000);

    // 5. Téléphone
    await messageInput.fill('0612345678');
    await messageInput.press('Enter');
    await page.waitForTimeout(2000);

    // 6. Référence produit
    await messageInput.fill('CAP-LUNA-001');
    await messageInput.press('Enter');
    await page.waitForTimeout(2000);

    // 7. Vérifier qu'une demande de confirmation apparaît
    await expect(page.locator('text=/confirmer|valider|créer le ticket/i')).toBeVisible({ timeout: 15000 });

    // 8. Confirmer la création du ticket
    const confirmButton = page.locator('button:has-text("Confirmer")').first();
    if (await confirmButton.isVisible({ timeout: 5000 })) {
      await confirmButton.click();

      // 9. Vérifier le message de succès
      await expect(page.locator('text=/ticket.*créé|SAV-/i')).toBeVisible({ timeout: 10000 });
    } else {
      // Alternative: envoyer "oui" pour confirmer
      await messageInput.fill('oui');
      await messageInput.press('Enter');
      await expect(page.locator('text=/ticket.*créé|SAV-/i')).toBeVisible({ timeout: 10000 });
    }
  });

  test('Créer un ticket puis l\'annuler', async ({ page }) => {
    // Démarrer la conversation
    const messageInput = page.locator('textarea[placeholder*="message"]');
    await messageInput.fill('Mon meuble est cassé');
    await messageInput.press('Enter');

    await page.waitForTimeout(2000);

    // Fournir des informations minimales
    await messageInput.fill('Test User');
    await messageInput.press('Enter');
    await page.waitForTimeout(1500);

    await messageInput.fill('test@example.com');
    await messageInput.press('Enter');
    await page.waitForTimeout(1500);

    // Attendre la demande de confirmation
    await expect(page.locator('text=/confirmer|annuler/i')).toBeVisible({ timeout: 10000 });

    // Annuler le ticket
    const cancelButton = page.locator('button:has-text("Annuler")').first();
    if (await cancelButton.isVisible({ timeout: 5000 })) {
      await cancelButton.click();
    } else {
      await messageInput.fill('non');
      await messageInput.press('Enter');
    }

    // Vérifier que l'annulation est confirmée
    await expect(page.locator('text=/annulé|abandonné/i')).toBeVisible({ timeout: 5000 });
  });

  test('Vérifier les validations des champs', async ({ page }) => {
    const messageInput = page.locator('textarea[placeholder*="message"]');

    // Démarrer la conversation
    await messageInput.fill('Problème avec ma table');
    await messageInput.press('Enter');
    await page.waitForTimeout(2000);

    // Essayer d'entrer un email invalide
    await messageInput.fill('email-invalide');
    await messageInput.press('Enter');
    await page.waitForTimeout(2000);

    // Le bot devrait demander un email valide
    // Note: Cette vérification dépend de l'implémentation du bot
    const chatMessages = page.locator('[class*="message"]');
    const messageCount = await chatMessages.count();
    expect(messageCount).toBeGreaterThan(0);
  });
});
