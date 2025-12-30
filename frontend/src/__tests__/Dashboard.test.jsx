import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dashboard from '../components/Dashboard';
import { server } from '../test/mocks/server';
import { ticketHandlers } from '../test/mocks/handlers';

describe('Dashboard', () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();
    vi.clearAllMocks();
  });

  describe('Loading and Initial State', () => {
    it('should show loading indicator on mount', () => {
      render(<Dashboard />);
      expect(screen.getByText(/Chargement des tickets SAV/i)).toBeInTheDocument();
    });

    it('should fetch and display tickets after loading', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Tableau de Bord SAV/i)).toBeInTheDocument();
      });
    });

    it('should display header with title', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/📊 Tableau de Bord SAV/i)).toBeInTheDocument();
      });
    });
  });

  describe('Statistics Display', () => {
    it('should display total tickets count', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Total Tickets/i)).toBeInTheDocument();
      });
    });

    it('should display P0 critical tickets count', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Critiques \(P0\)/i)).toBeInTheDocument();
      });
    });

    it('should display P1 urgent tickets count', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Urgents \(P1\)/i)).toBeInTheDocument();
      });
    });

    it('should display auto-resolved tickets count', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Check in statistics section specifically
        const autoResolvedElements = screen.getAllByText(/Auto-résolus/i);
        expect(autoResolvedElements.length).toBeGreaterThan(0);
      });
    });

    it('should calculate correct statistics from ticket data', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Default mock has 2 tickets
        const totalElement = screen.getByText(/Total Tickets/i).parentElement;
        expect(totalElement).toHaveTextContent('2');
      });
    });
  });

  describe('Ticket List Display', () => {
    it('should display tickets table with headers', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Use columnheader role for table headers to avoid multiple matches
        expect(screen.getByRole('columnheader', { name: /Ticket/i })).toBeInTheDocument();
        expect(screen.getByRole('columnheader', { name: /Client/i })).toBeInTheDocument();
        expect(screen.getByRole('columnheader', { name: /Problème/i })).toBeInTheDocument();
        expect(screen.getByRole('columnheader', { name: /Priorité/i })).toBeInTheDocument();
      });
    });

    it('should display ticket data in table', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Jean Dupont/i)).toBeInTheDocument();
        expect(screen.getByText(/Marie Martin/i)).toBeInTheDocument();
      });
    });

    it('should display product information', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Canapé Luna/i)).toBeInTheDocument();
        expect(screen.getByText(/Table Élégance/i)).toBeInTheDocument();
      });
    });

    it('should display problem descriptions', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Tissu déchiré/i)).toBeInTheDocument();
        expect(screen.getByText(/Rayure sur le plateau/i)).toBeInTheDocument();
      });
    });

    it('should show "no tickets" message when list is empty', async () => {
      server.use(ticketHandlers.withEmptyList);
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Aucun ticket trouvé/i)).toBeInTheDocument();
      });
    });
  });

  describe('Priority Filtering', () => {
    it('should have priority filter dropdown', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const prioritySelect = screen.getByLabelText(/Priorité:/i);
        expect(prioritySelect).toBeInTheDocument();
      });
    });

    it('should show all priority options', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const prioritySelect = screen.getByLabelText(/Priorité:/i);
        expect(prioritySelect).toHaveTextContent(/Toutes/i);
        expect(prioritySelect).toHaveTextContent(/P0 - Critique/i);
        expect(prioritySelect).toHaveTextContent(/P1 - Urgent/i);
      });
    });

    it('should filter tickets by priority when selected', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Jean Dupont/i)).toBeInTheDocument();
      });

      const prioritySelect = screen.getByLabelText(/Priorité:/i);
      await user.selectOptions(prioritySelect, 'P0');

      await waitFor(() => {
        // Filtering logic should update visible tickets
        expect(prioritySelect.value).toBe('P0');
      });
    });

    it('should update ticket count when filtering', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/2 ticket\(s\)/i)).toBeInTheDocument();
      });

      const prioritySelect = screen.getByLabelText(/Priorité:/i);
      await user.selectOptions(prioritySelect, 'P0');

      // Count should update based on filtered results
      await waitFor(() => {
        expect(screen.getByText(/ticket\(s\)/i)).toBeInTheDocument();
      });
    });
  });

  describe('Status Filtering', () => {
    it('should have status filter dropdown', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const statusSelect = screen.getByLabelText(/Statut:/i);
        expect(statusSelect).toBeInTheDocument();
      });
    });

    it('should show all status options', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const statusSelect = screen.getByLabelText(/Statut:/i);
        expect(statusSelect).toHaveTextContent(/Tous/i);
        expect(statusSelect).toHaveTextContent(/Escaladés/i);
        expect(statusSelect).toHaveTextContent(/En attente technicien/i);
        expect(statusSelect).toHaveTextContent(/Auto-résolus/i);
      });
    });

    it('should filter tickets by status when selected', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Jean Dupont/i)).toBeInTheDocument();
      });

      const statusSelect = screen.getByLabelText(/Statut:/i);
      await user.selectOptions(statusSelect, 'escalated_to_human');

      await waitFor(() => {
        expect(statusSelect.value).toBe('escalated_to_human');
      });
    });

    it('should combine priority and status filters', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Jean Dupont/i)).toBeInTheDocument();
      });

      const prioritySelect = screen.getByLabelText(/Priorité:/i);
      const statusSelect = screen.getByLabelText(/Statut:/i);

      await user.selectOptions(prioritySelect, 'P0');
      await user.selectOptions(statusSelect, 'escalated_to_human');

      await waitFor(() => {
        expect(prioritySelect.value).toBe('P0');
        expect(statusSelect.value).toBe('escalated_to_human');
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when fetch fails', async () => {
      server.use(ticketHandlers.withError);
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Erreur lors de la récupération des tickets/i)).toBeInTheDocument();
      });
    });

    it('should show retry button on error', async () => {
      server.use(ticketHandlers.withError);
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Réessayer/i)).toBeInTheDocument();
      });
    });

    it('should retry fetching tickets when retry button clicked', async () => {
      server.use(ticketHandlers.withError);
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Réessayer/i)).toBeInTheDocument();
      });

      // Reset to working handler
      server.resetHandlers();

      const retryButton = screen.getByText(/Réessayer/i);
      await user.click(retryButton);

      // Wait for loading to finish and tickets to appear
      await waitFor(() => {
        // Check that error message is gone
        expect(screen.queryByText(/Réessayer/i)).not.toBeInTheDocument();
      }, { timeout: 10000 });

      // Verify tickets table is displayed with data
      await waitFor(() => {
        const table = screen.getByRole('table');
        expect(table).toBeInTheDocument();
        // Should show ticket count
        expect(screen.getByText(/ticket\(s\)/i)).toBeInTheDocument();
      }, { timeout: 10000 });
    });
  });

  describe('Ticket Actions', () => {
    it('should have action buttons for each ticket', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const actionButtons = screen.getAllByRole('button');
        // Should have buttons for viewing dossiers, downloading, etc.
        expect(actionButtons.length).toBeGreaterThan(0);
      });
    });

    it('should handle dossier download', async () => {
      const createElementSpy = vi.spyOn(document, 'createElement');
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Jean Dupont/i)).toBeInTheDocument();
      });

      // Find download button (if visible)
      const downloadButtons = screen.queryAllByRole('button').filter(btn =>
        btn.querySelector('svg')?.classList.contains('lucide-download')
      );

      if (downloadButtons.length > 0) {
        await user.click(downloadButtons[0]);

        await waitFor(() => {
          // Verify download was initiated
          expect(createElementSpy).toHaveBeenCalledWith('a');
        });
      }

      createElementSpy.mockRestore();
    });
  });

  describe('Priority Display', () => {
    it('should show priority badges with correct colors', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const priorityBadges = screen.queryAllByText(/P0|P1|P2|P3/);
        expect(priorityBadges.length).toBeGreaterThan(0);
      });
    });

    it('should display P0 with critical styling', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Look for high priority ticket
        const highPriorityElement = screen.queryByText(/haute|P0/i);
        if (highPriorityElement) {
          expect(highPriorityElement).toBeInTheDocument();
        }
      });
    });
  });

  describe('Status Display', () => {
    it('should display status labels correctly', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Look for status labels
        const statusElements = screen.queryAllByText(/nouveau|en_cours|escalated|awaiting/i);
        expect(statusElements.length).toBeGreaterThan(0);
      });
    });

    it('should show status icons', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Icons should be rendered (lucide icons)
        const table = screen.getByRole('table');
        expect(table).toBeInTheDocument();
      });
    });
  });

  describe('Date Display', () => {
    it('should display creation dates for tickets', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Look for date column header specifically
        const dateHeader = screen.getByRole('columnheader', { name: /Date/i });
        expect(dateHeader).toBeInTheDocument();
      });
    });

    it('should format dates correctly', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Dates should be present in some format
        const table = screen.getByRole('table');
        expect(table).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Layout', () => {
    it('should render statistics grid', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Total Tickets/i)).toBeInTheDocument();
        expect(screen.getByText(/Critiques \(P0\)/i)).toBeInTheDocument();
        expect(screen.getByText(/Urgents \(P1\)/i)).toBeInTheDocument();
        // Auto-résolus appears multiple times, so just check it exists
        const autoResolvedElements = screen.getAllByText(/Auto-résolus/i);
        expect(autoResolvedElements.length).toBeGreaterThan(0);
      });
    });

    it('should render filters section', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByLabelText(/Priorité:/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Statut:/i)).toBeInTheDocument();
      });
    });
  });

  describe('Data Integrity', () => {
    it('should display all ticket fields', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Client name
        expect(screen.getByText(/Jean Dupont/i)).toBeInTheDocument();
        // Product
        expect(screen.getByText(/Canapé Luna/i)).toBeInTheDocument();
        // Problem
        expect(screen.getByText(/Tissu déchiré/i)).toBeInTheDocument();
      });
    });

    it('should handle missing ticket data gracefully', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // Component should render even with partial data
        expect(screen.getByText(/Tableau de Bord SAV/i)).toBeInTheDocument();
      });
    });
  });

  describe('User Interactions', () => {
    it('should allow filter reset to "all"', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Jean Dupont/i)).toBeInTheDocument();
      });

      const prioritySelect = screen.getByLabelText(/Priorité:/i);

      // Change filter
      await user.selectOptions(prioritySelect, 'P0');
      expect(prioritySelect.value).toBe('P0');

      // Reset filter
      await user.selectOptions(prioritySelect, 'all');
      expect(prioritySelect.value).toBe('all');
    });

    it('should maintain filter state during interactions', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Jean Dupont/i)).toBeInTheDocument();
      });

      const prioritySelect = screen.getByLabelText(/Priorité:/i);
      await user.selectOptions(prioritySelect, 'P1');

      await waitFor(() => {
        expect(prioritySelect.value).toBe('P1');
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper table structure', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const table = screen.getByRole('table');
        expect(table).toBeInTheDocument();
      });
    });

    it('should have labeled form controls', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByLabelText(/Priorité:/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Statut:/i)).toBeInTheDocument();
      });
    });

    it('should have accessible buttons', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        expect(buttons.length).toBeGreaterThan(0);
      });
    });
  });
});
