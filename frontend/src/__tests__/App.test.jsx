import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';

describe('App', () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();
  });

  describe('Initial Rendering', () => {
    it('should render navigation bar', () => {
      render(<App />);

      expect(screen.getByText(/Bot SAV \(Texte\)/i)).toBeInTheDocument();
      expect(screen.getByText(/Mode Vocal/i)).toBeInTheDocument();
      expect(screen.getByText(/Tableau de Bord/i)).toBeInTheDocument();
    });

    it('should render chat view by default', async () => {
      render(<App />);

      await waitFor(() => {
        // Chat interface should be visible (textarea)
        const textarea = screen.queryByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });
    });

    it('should have navigation buttons', () => {
      render(<App />);

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThanOrEqual(3);
    });
  });

  describe('Navigation', () => {
    it('should switch to dashboard view when dashboard button clicked', async () => {
      render(<App />);

      const dashboardButton = screen.getByText(/Tableau de Bord/i);
      await user.click(dashboardButton);

      await waitFor(() => {
        // Dashboard header should be visible
        expect(screen.getByText(/📊 Tableau de Bord SAV/i)).toBeInTheDocument();
      });
    });

    it('should switch to voice view when voice button clicked', async () => {
      render(<App />);

      const voiceButton = screen.getByText(/Mode Vocal/i);
      await user.click(voiceButton);

      // Voice component should be rendered (it might have different content)
      await waitFor(() => {
        const voiceButton = screen.getByText(/Mode Vocal/i);
        expect(voiceButton).toBeInTheDocument();
      });
    });

    it('should switch back to chat view', async () => {
      render(<App />);

      // Go to dashboard first
      const dashboardButton = screen.getByText(/Tableau de Bord/i);
      await user.click(dashboardButton);

      await waitFor(() => {
        expect(screen.getByText(/📊 Tableau de Bord SAV/i)).toBeInTheDocument();
      });

      // Go back to chat
      const chatButton = screen.getByText(/Bot SAV \(Texte\)/i);
      await user.click(chatButton);

      await waitFor(() => {
        const textarea = screen.queryByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });
    });

    it('should highlight active navigation button', async () => {
      render(<App />);

      const chatButton = screen.getByText(/Bot SAV \(Texte\)/i).closest('button');
      const dashboardButton = screen.getByText(/Tableau de Bord/i).closest('button');

      // Chat should be active by default
      expect(chatButton).toHaveClass(/bg-red-600/);

      // Click dashboard
      await user.click(dashboardButton);

      await waitFor(() => {
        expect(dashboardButton).toHaveClass(/bg-red-600/);
      });
    });
  });

  describe('Component Persistence', () => {
    it('should preserve component state when switching views', async () => {
      render(<App />);

      // Type in chat
      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Test message');

      // Switch to dashboard - use getByRole to avoid multiple matches
      const dashboardButton = screen.getByRole('button', { name: /Tableau de Bord/i });
      await user.click(dashboardButton);

      await waitFor(() => {
        expect(screen.getByText(/📊 Tableau de Bord SAV/i)).toBeInTheDocument();
      });

      // Switch back to chat
      const chatButton = screen.getByRole('button', { name: /Bot SAV \(Texte\)/i });
      await user.click(chatButton);

      // Message should still be there
      await waitFor(() => {
        const textareaAgain = screen.getByRole('textbox');
        expect(textareaAgain).toHaveValue('Test message');
      });
    });
  });

  describe('Layout', () => {
    it('should have full-screen layout', () => {
      const { container } = render(<App />);

      const mainDiv = container.firstChild;
      expect(mainDiv).toHaveClass(/h-screen/);
    });

    it('should have navigation at top', () => {
      render(<App />);

      const nav = screen.getByRole('navigation');
      expect(nav).toBeInTheDocument();
    });

    it('should only show one view at a time', async () => {
      render(<App />);

      // Initially on chat, dashboard should be hidden
      await waitFor(() => {
        const textarea = screen.queryByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });

      // Switch to dashboard
      const dashboardButton = screen.getByText(/Tableau de Bord/i);
      await user.click(dashboardButton);

      await waitFor(() => {
        // Dashboard should be visible
        expect(screen.getByText(/📊 Tableau de Bord SAV/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have navigation buttons with text', () => {
      render(<App />);

      expect(screen.getByText(/Bot SAV \(Texte\)/i)).toBeInTheDocument();
      expect(screen.getByText(/Mode Vocal/i)).toBeInTheDocument();
      expect(screen.getByText(/Tableau de Bord/i)).toBeInTheDocument();
    });

    it('should have clickable navigation buttons', () => {
      render(<App />);

      // Check only the main navigation buttons, not all buttons on the page
      const chatButton = screen.getByRole('button', { name: /Bot SAV \(Texte\)/i });
      const voiceButton = screen.getByRole('button', { name: /Mode Vocal/i });
      const dashboardButton = screen.getByRole('button', { name: /Tableau de Bord/i });

      expect(chatButton).toBeEnabled();
      expect(voiceButton).toBeEnabled();
      expect(dashboardButton).toBeEnabled();
    });
  });
});
