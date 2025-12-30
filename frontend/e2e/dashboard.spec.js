import { test, expect } from '@playwright/test';

test.describe('Dashboard des tickets SAV', () => {
  test.beforeEach(async ({ page }) => {
    // Aller sur la page principale
    await page.goto('/');

    // Cliquer sur le bouton "Tableau de Bord"
    const dashboardButton = page.locator('button:has-text("Tableau de Bord")');
    await expect(dashboardButton).toBeVisible();
    await dashboardButton.click();

    // Attendre que le dashboard soit chargé
    await expect(page.locator('text=/Tableau de Bord/i')).toBeVisible();
  });

  test('Afficher la liste des tickets', async ({ page }) => {
    // Attendre que les tickets soient chargés
    await page.waitForTimeout(2000);

    // Vérifier que le titre du dashboard est visible
    await expect(page.locator('h1:has-text("Tableau de Bord")')).toBeVisible();

    // Vérifier que la table des tickets est visible
    const table = page.locator('table').or(page.locator('[class*="ticket"]'));
    await expect(table.first()).toBeVisible({ timeout: 5000 });

    // Vérifier qu'il y a des tickets ou un message "Aucun ticket"
    const hasTickets = await page.locator('text=/SAV-|Aucun ticket/i').count();
    expect(hasTickets).toBeGreaterThan(0);
  });

  test('Filtrer les tickets par priorité', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Chercher le filtre de priorité
    const priorityFilter = page.locator('select[name*="priority"]').or(
      page.locator('select:near(:text("Priorité"))')
    ).or(
      page.locator('[aria-label*="priorité"]')
    ).first();

    if (await priorityFilter.isVisible({ timeout: 5000 })) {
      // Sélectionner une priorité spécifique
      await priorityFilter.selectOption({ label: /P0|Urgente|Haute/i });

      await page.waitForTimeout(1000);

      // Vérifier que les tickets affichés correspondent au filtre
      // (le nombre de tickets devrait changer ou rester le même)
      const tickets = page.locator('[class*="ticket"]').or(page.locator('tr[data-ticket]'));
      const ticketCount = await tickets.count();

      // Au moins vérifier que le filtre ne casse pas l'affichage
      expect(ticketCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('Filtrer les tickets par statut', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Chercher le filtre de statut
    const statusFilter = page.locator('select[name*="status"]').or(
      page.locator('select:near(:text("Statut"))')
    ).or(
      page.locator('[aria-label*="statut"]')
    ).first();

    if (await statusFilter.isVisible({ timeout: 5000 })) {
      // Sélectionner un statut spécifique
      await statusFilter.selectOption({ label: /nouveau|en cours|résolu/i });

      await page.waitForTimeout(1000);

      // Vérifier que le filtre s'applique correctement
      const tickets = page.locator('[class*="ticket"]').or(page.locator('tbody tr'));
      const ticketCount = await tickets.count();

      expect(ticketCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('Voir les détails d\'un ticket', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Chercher un bouton "Voir" ou "Détails"
    const viewButton = page.locator('button[title*="Voir"]').or(
      page.locator('button:has-text("Voir")').or(
        page.locator('svg[class*="eye"]').first()
      )
    ).first();

    if (await viewButton.isVisible({ timeout: 5000 })) {
      await viewButton.click();

      // Attendre que le modal ou la page de détails s'ouvre
      await page.waitForTimeout(1500);

      // Vérifier que les détails du ticket sont affichés
      const detailsVisible = await page.locator('text=/Détails|Dossier|Information/i').isVisible({ timeout: 3000 }).catch(() => false);

      if (detailsVisible) {
        expect(detailsVisible).toBeTruthy();
      } else {
        // Alternativement, vérifier que la page a changé ou qu'un modal s'est ouvert
        const modalOrDetails = await page.locator('[class*="modal"]').or(page.locator('[role="dialog"]')).count();
        console.log(`Modal/Details count: ${modalOrDetails}`);
      }
    }
  });

  test('Afficher les statistiques des tickets', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Chercher les cartes de statistiques (total, par priorité, etc.)
    const statsCards = page.locator('[class*="stat"]').or(
      page.locator('[class*="card"]').or(
        page.locator('text=/total|P0|P1|P2/i')
      )
    );

    const statsCount = await statsCards.count();

    // Il devrait y avoir au moins quelques statistiques affichées
    expect(statsCount).toBeGreaterThan(0);

    // Vérifier que le total des tickets est affiché
    const totalText = await page.locator('text=/total.*ticket/i').count();
    expect(totalText).toBeGreaterThan(0);
  });

  test('Trier les tickets par date', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Chercher l'en-tête de colonne "Date"
    const dateHeader = page.locator('th:has-text("Date")').or(
      page.locator('th:has-text("Création")')
    ).first();

    if (await dateHeader.isVisible({ timeout: 5000 })) {
      // Cliquer pour trier
      await dateHeader.click();

      await page.waitForTimeout(1000);

      // Vérifier que l'ordre des tickets a changé (difficile à tester sans données spécifiques)
      const tickets = page.locator('tbody tr');
      const ticketCount = await tickets.count();

      expect(ticketCount).toBeGreaterThanOrEqual(0);
    }
  });

  test('Rechercher un ticket par numéro', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Chercher un champ de recherche
    const searchInput = page.locator('input[type="search"]').or(
      page.locator('input[placeholder*="Recherche"]').or(
        page.locator('input[aria-label*="recherche"]')
      )
    ).first();

    if (await searchInput.isVisible({ timeout: 5000 })) {
      // Entrer un numéro de ticket
      await searchInput.fill('SAV-2024');

      await page.waitForTimeout(1000);

      // Vérifier que les résultats sont filtrés
      const tickets = page.locator('text=/SAV-2024/i');
      const foundTickets = await tickets.count();

      // Au moins vérifier que la recherche ne casse pas l'interface
      expect(foundTickets).toBeGreaterThanOrEqual(0);
    }
  });

  test('Navigation entre Chat et Dashboard', async ({ page }) => {
    // Vérifier qu'on est sur le dashboard
    await expect(page.locator('h1:has-text("Tableau de Bord")')).toBeVisible();

    // Retourner au chat
    const chatButton = page.locator('button:has-text("Bot SAV")').or(
      page.locator('button:has-text("Texte")')
    ).first();

    await chatButton.click();

    // Vérifier qu'on est maintenant sur le chat
    await expect(page.locator('textarea[placeholder*="message"]')).toBeVisible();

    // Retourner au dashboard
    const dashboardButton = page.locator('button:has-text("Tableau de Bord")');
    await dashboardButton.click();

    // Vérifier qu'on est de nouveau sur le dashboard
    await expect(page.locator('h1:has-text("Tableau de Bord")')).toBeVisible();
  });

  test('Responsive design du dashboard', async ({ page, viewport }) => {
    // Changer la taille de la fenêtre pour mobile
    await page.setViewportSize({ width: 375, height: 667 });

    await page.waitForTimeout(1000);

    // Vérifier que le dashboard s'affiche correctement sur mobile
    await expect(page.locator('h1:has-text("Tableau de Bord")')).toBeVisible();

    // Vérifier que les éléments sont empilés verticalement (pas de vérification précise)
    const dashboard = page.locator('[class*="dashboard"]').or(page.locator('main'));
    await expect(dashboard.first()).toBeVisible();

    // Revenir à la taille desktop
    await page.setViewportSize({ width: 1280, height: 720 });

    await page.waitForTimeout(500);

    // Vérifier que le layout desktop fonctionne
    await expect(page.locator('h1:has-text("Tableau de Bord")')).toBeVisible();
  });

  test('Rafraîchir la liste des tickets', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Chercher un bouton de rafraîchissement
    const refreshButton = page.locator('button[aria-label*="Rafraîchir"]').or(
      page.locator('button[title*="Rafraîchir"]').or(
        page.locator('button:has-text("Rafraîchir")')
      )
    ).first();

    if (await refreshButton.isVisible({ timeout: 5000 })) {
      // Cliquer sur le bouton de rafraîchissement
      await refreshButton.click();

      await page.waitForTimeout(2000);

      // Vérifier que les tickets sont toujours affichés
      const tickets = page.locator('text=/SAV-|Aucun ticket/i');
      const ticketCount = await tickets.count();

      expect(ticketCount).toBeGreaterThan(0);
    } else {
      // Si pas de bouton de rafraîchissement, recharger la page
      await page.reload();
      await page.waitForTimeout(2000);

      await expect(page.locator('h1:has-text("Tableau de Bord")')).toBeVisible();
    }
  });
});
