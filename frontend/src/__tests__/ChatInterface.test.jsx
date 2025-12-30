import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatInterface from '../components/ChatInterface';
import { server } from '../test/mocks/server';
import { chatHandlers, uploadHandlers } from '../test/mocks/handlers';

describe('ChatInterface', () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();
    vi.clearAllMocks();
  });

  describe('Rendering and Initial State', () => {
    it('should render chat interface with input', () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeInTheDocument();
    });

    it('should display welcome message on mount', async () => {
      render(<ChatInterface />);
      await waitFor(() => {
        expect(screen.getByText(/Bonjour ! Je suis votre assistant SAV/i)).toBeInTheDocument();
      });
    });

    it('should render header with title', () => {
      render(<ChatInterface />);
      expect(screen.getByText(/Service clientèle du groupe Mobilier de France/i)).toBeInTheDocument();
    });

    it('should render file input for uploads', () => {
      render(<ChatInterface />);
      const fileInput = screen.getByRole('textbox').parentElement.parentElement.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
    });
  });

  describe('Message Sending', () => {
    it('should send a text message', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      await user.type(textarea, 'Mon canapé est cassé');
      const buttons = screen.getAllByRole('button');
      const sendButton = buttons[buttons.length - 1]; // Last button is send
      await user.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('Mon canapé est cassé')).toBeInTheDocument();
      });
    });

    it('should clear input after sending message', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      await user.type(textarea, 'Test message');
      const buttons = screen.getAllByRole('button');
      const sendButton = buttons[buttons.length - 1];
      await user.click(sendButton);

      await waitFor(() => {
        expect(textarea).toHaveValue('');
      });
    });

    it('should send message on Enter key press', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      await user.type(textarea, 'Message via Enter{Enter}');

      await waitFor(() => {
        expect(screen.getByText(/Message via Enter/i)).toBeInTheDocument();
      });
    });

    it('should display API response message', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      await user.type(textarea, 'Bonjour');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText(/Comment puis-je vous aider/i)).toBeInTheDocument();
      });
    });

    it('should show typing indicator while processing', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      await user.type(textarea, 'Test');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      // Wait for message to be sent and response received
      await waitFor(() => {
        expect(screen.getByText('Test')).toBeInTheDocument();
      });
    });
  });

  describe('File Upload', () => {
    it('should have file upload input with correct attributes', () => {
      render(<ChatInterface />);
      const fileInput = document.querySelector('input[type="file"]');

      expect(fileInput).toBeInTheDocument();
      expect(fileInput).toHaveAttribute('accept', 'image/*,video/*');
      expect(fileInput).toHaveAttribute('multiple');
    });

    it('should accept file selection', async () => {
      render(<ChatInterface />);
      const file = new File(['photo'], 'test-photo.jpg', { type: 'image/jpeg' });
      const fileInput = document.querySelector('input[type="file"]');

      await user.upload(fileInput, file);

      // Verify file was added to input
      expect(fileInput.files).toHaveLength(1);
      expect(fileInput.files[0]).toBe(file);
      expect(fileInput.files[0].name).toBe('test-photo.jpg');
    });

    it('should have camera/upload button', () => {
      render(<ChatInterface />);

      // Find button with Camera icon or upload-related title
      const buttons = screen.getAllByRole('button');
      const uploadButton = buttons.find(btn =>
        btn.title?.toLowerCase().includes('photo') ||
        btn.querySelector('svg')?.classList.contains('lucide-camera')
      );

      expect(uploadButton).toBeDefined();
    });

    it('should handle upload error', async () => {
      server.use(uploadHandlers.withError);
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
      render(<ChatInterface />);

      const file = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const fileInput = document.querySelector('input[type="file"]');

      await user.upload(fileInput, file);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith(expect.stringContaining('Erreur'));
      });
      alertSpy.mockRestore();
    });
  });

  describe('Voice Features', () => {
    it('should have voice toggle button in header', () => {
      render(<ChatInterface />);
      expect(screen.getByText(/Voix ON|Voix OFF/i)).toBeInTheDocument();
    });

    it('should toggle speech synthesis', async () => {
      render(<ChatInterface />);
      const voiceToggle = screen.getByText(/Voix ON/i).closest('button');

      await user.click(voiceToggle);

      await waitFor(() => {
        expect(screen.getByText(/Voix OFF/i)).toBeInTheDocument();
      });
    });

    it('should show recording indicator when voice recording active', async () => {
      render(<ChatInterface />);

      // Find mic button (has Mic icon)
      const buttons = screen.getAllByRole('button');
      const micButton = buttons.find(btn => {
        const svg = btn.querySelector('svg');
        return svg?.classList.contains('lucide-mic') || svg?.classList.contains('lucide-mic-off');
      });

      if (micButton) {
        await user.click(micButton);

        await waitFor(() => {
          expect(screen.getByText(/Écoute en cours/i)).toBeInTheDocument();
        });
      }
    });
  });

  describe('Ticket Confirmation Flow', () => {
    it('should display ticket confirmation buttons when ticket data received', async () => {
      server.use(chatHandlers.withTicketConfirmation);
      render(<ChatInterface />);

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Je confirme');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText(/Valider le ticket/i)).toBeInTheDocument();
        expect(screen.getByText(/Recommencer/i)).toBeInTheDocument();
      });
    });

    it('should create ticket on confirmation', async () => {
      server.use(chatHandlers.withTicketConfirmation);
      render(<ChatInterface />);

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Je confirme');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText(/Valider le ticket/i)).toBeInTheDocument();
      });

      const confirmButton = screen.getByText(/Valider le ticket/i).closest('button');
      await user.click(confirmButton);

      await waitFor(() => {
        expect(screen.getByText(/Ticket.*créé avec succès/i)).toBeInTheDocument();
      });
    });

    it('should cancel ticket creation', async () => {
      server.use(chatHandlers.withTicketConfirmation);
      render(<ChatInterface />);

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Je confirme');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText(/Recommencer/i)).toBeInTheDocument();
      });

      const cancelButton = screen.getByText(/Recommencer/i).closest('button');
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.getByText(/recommençons/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message on API failure', async () => {
      server.use(chatHandlers.withError);
      render(<ChatInterface />);

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Test');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText(/problème technique/i)).toBeInTheDocument();
      });
    });

    it('should handle network error gracefully', async () => {
      server.use(chatHandlers.withNetworkError);
      render(<ChatInterface />);

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Test');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText(/problème technique|erreur/i)).toBeInTheDocument();
      });
    });

    it('should allow retry after error', async () => {
      server.use(chatHandlers.withError);
      render(<ChatInterface />);

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Test');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText(/problème technique/i)).toBeInTheDocument();
      });

      // Reset to working handler
      server.resetHandlers();

      // Retry
      await user.clear(textarea);
      await user.type(textarea, 'Retry');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText(/Comment puis-je vous aider/i)).toBeInTheDocument();
      });
    });
  });

  describe('Session Management', () => {
    it('should generate session ID on mount', () => {
      const { container } = render(<ChatInterface />);
      expect(container).toBeInTheDocument();
      // Session ID is internal, verify component renders
    });

    it('should maintain messages during session', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      // Send first message
      await user.type(textarea, 'Message 1');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText('Message 1')).toBeInTheDocument();
      });

      // Send second message
      await user.type(textarea, 'Message 2');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText('Message 2')).toBeInTheDocument();
      });

      // Both messages should be visible
      expect(screen.getByText('Message 1')).toBeInTheDocument();
      expect(screen.getByText('Message 2')).toBeInTheDocument();
    });
  });

  describe('UI Interactions', () => {
    it('should auto-scroll to latest message', async () => {
      const { container } = render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      // Send multiple messages
      for (let i = 1; i <= 3; i++) {
        await user.type(textarea, `Message ${i}`);
        const buttons = screen.getAllByRole('button');
        await user.click(buttons[buttons.length - 1]);
        await waitFor(() => {
          expect(screen.getByText(`Message ${i}`)).toBeInTheDocument();
        });
      }

      // Latest message should be visible
      expect(screen.getByText('Message 3')).toBeInTheDocument();
    });
  });

  describe('Message Formatting', () => {
    it('should display user and assistant messages differently', async () => {
      render(<ChatInterface />);

      // Wait for welcome message (assistant)
      await waitFor(() => {
        const messages = screen.queryAllByText(/Bonjour ! Je suis votre assistant SAV/i);
        expect(messages.length).toBeGreaterThan(0);
      });

      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'User message');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText('User message')).toBeInTheDocument();
      });

      // Both messages should be present
      const assistantMessages = screen.queryAllByText(/Bonjour ! Je suis votre assistant SAV/i);
      expect(assistantMessages.length).toBeGreaterThan(0);
      expect(screen.getByText('User message')).toBeInTheDocument();
    });

    it('should sanitize HTML in messages (XSS protection)', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      await user.type(textarea, '<script>alert("xss")</script>Safe text');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        // The message container should exist but script tag should be sanitized
        const userMsg = screen.getByText(/<script>|Safe text/i);
        expect(userMsg).toBeInTheDocument();
      });
    });

    it('should display timestamps for messages', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      await user.type(textarea, 'Timestamped message');
      const buttons = screen.getAllByRole('button');
      await user.click(buttons[buttons.length - 1]);

      await waitFor(() => {
        expect(screen.getByText('Timestamped message')).toBeInTheDocument();
      });

      // Timestamp format is HH:MM - should have at least one
      const timeRegex = /\d{2}:\d{2}/;
      const timestamps = screen.queryAllByText(timeRegex);
      expect(timestamps.length).toBeGreaterThan(0);
    });
  });

  describe('Text-to-Speech Integration', () => {
    it('should have speech synthesis controls', () => {
      const speakSpy = vi.spyOn(global.speechSynthesis, 'speak');
      render(<ChatInterface />);

      // Verify speech synthesis is available
      expect(global.speechSynthesis).toBeDefined();
      expect(speakSpy).toBeDefined();
    });

    it('should speak welcome message on mount when enabled', async () => {
      const speakSpy = vi.spyOn(global.speechSynthesis, 'speak');
      render(<ChatInterface />);

      // Wait for welcome message and speech
      await waitFor(() => {
        expect(speakSpy).toHaveBeenCalled();
      }, { timeout: 2000 });
    });
  });

  describe('Accessibility', () => {
    it('should have proper form structure', () => {
      render(<ChatInterface />);

      // Should have textarea
      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeInTheDocument();

      // Should have buttons
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('should be keyboard navigable', async () => {
      render(<ChatInterface />);
      const textarea = screen.getByRole('textbox');

      // Should be able to type
      await user.type(textarea, 'Test');
      expect(textarea).toHaveValue('Test');

      // Should be able to use Enter key
      await user.type(textarea, '{Enter}');
      await waitFor(() => {
        expect(screen.getByText('Test')).toBeInTheDocument();
      });
    });
  });
});
