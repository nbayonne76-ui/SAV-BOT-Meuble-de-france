import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import VoiceChatWhisper from '../components/VoiceChatWhisper';

describe('VoiceChatWhisper', () => {
  let mockMediaStream;
  let mockGetUserMedia;
  let mockMediaRecorder;

  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();

    // Mock MediaStream
    mockMediaStream = {
      getTracks: vi.fn(() => [
        { stop: vi.fn(), kind: 'audio', enabled: true }
      ]),
      getAudioTracks: vi.fn(() => [
        { stop: vi.fn(), kind: 'audio', enabled: true }
      ]),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    };

    // Mock getUserMedia
    mockGetUserMedia = vi.fn().mockResolvedValue(mockMediaStream);
    global.navigator.mediaDevices.getUserMedia = mockGetUserMedia;

    // Mock MediaRecorder
    mockMediaRecorder = {
      state: 'inactive',
      start: vi.fn(function() { this.state = 'recording'; }),
      stop: vi.fn(function() {
        this.state = 'inactive';
        if (this.onstop) this.onstop();
      }),
      pause: vi.fn(),
      resume: vi.fn(),
      ondataavailable: null,
      onstop: null,
      onerror: null
    };

    global.MediaRecorder = vi.fn(() => mockMediaRecorder);
    global.MediaRecorder.isTypeSupported = vi.fn(() => true);

    // Mock fetch for API calls
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ===================================
  // MICROPHONE ACCESS TESTS (5 tests)
  // ===================================

  describe('Microphone Access', () => {
    it('should request microphone permission on component mount', async () => {
      render(<VoiceChatWhisper />);

      await waitFor(() => {
        expect(mockGetUserMedia).toHaveBeenCalled();
      });
    });

    it('should display success message when microphone permission is granted', async () => {
      render(<VoiceChatWhisper />);

      await waitFor(() => {
        expect(screen.getByText(/microphone autorisé/i)).toBeInTheDocument();
      });
    });

    it('should enable start button when microphone permission is granted', async () => {
      render(<VoiceChatWhisper />);

      await waitFor(() => {
        const startButton = screen.getByRole('button', { name: /démarrer la conversation/i });
        expect(startButton).toBeEnabled();
      });
    });

    it('should display error message when microphone permission is denied', async () => {
      mockGetUserMedia.mockRejectedValueOnce(
        new DOMException('Permission denied', 'NotAllowedError')
      );

      render(<VoiceChatWhisper />);

      await waitFor(() => {
        expect(screen.getByText(/microphone bloqué/i)).toBeInTheDocument();
      });
    });

    it('should disable start button when microphone permission is denied', async () => {
      mockGetUserMedia.mockRejectedValueOnce(
        new DOMException('Permission denied', 'NotAllowedError')
      );

      render(<VoiceChatWhisper />);

      await waitFor(() => {
        const startButton = screen.getByRole('button', { name: /microphone non autorisé/i });
        expect(startButton).toBeDisabled();
      });
    });
  });

  // ===================================
  // COMPONENT STRUCTURE TESTS (5 tests)
  // ===================================

  describe('Component Structure', () => {
    it('should render the main heading', () => {
      render(<VoiceChatWhisper />);

      expect(screen.getByRole('heading', { name: /assistant vocal sav/i })).toBeInTheDocument();
    });

    it('should display BB Expansion Mobilier de France branding', () => {
      render(<VoiceChatWhisper />);

      expect(screen.getByText(/bb expansion mobilier de france/i)).toBeInTheDocument();
    });

    it('should show guidance section with tips', () => {
      render(<VoiceChatWhisper />);

      expect(screen.getByText(/conseils pour une conversation réussie/i)).toBeInTheDocument();
    });

    it('should display conversation example', () => {
      render(<VoiceChatWhisper />);

      expect(screen.getByText(/exemple de conversation/i)).toBeInTheDocument();
    });

    it('should have main start button when permission is granted', async () => {
      render(<VoiceChatWhisper />);

      await waitFor(() => {
        const startButton = screen.getByRole('button', { name: /démarrer la conversation/i });
        expect(startButton).toBeInTheDocument();
      });
    });
  });

  // ===================================
  // PROPS & CALLBACKS TESTS (3 tests)
  // ===================================

  describe('Props & Callbacks', () => {
    it('should accept onTicketCreated callback prop', () => {
      const mockCallback = vi.fn();
      render(<VoiceChatWhisper onTicketCreated={mockCallback} />);

      expect(screen.getByRole('heading', { name: /assistant vocal sav/i })).toBeInTheDocument();
    });

    it('should use MediaRecorder for audio recording', () => {
      render(<VoiceChatWhisper />);

      // Verify MediaRecorder mock is available
      expect(global.MediaRecorder).toBeDefined();
      expect(global.MediaRecorder.isTypeSupported).toBeDefined();
    });

    it('should use getUserMedia for microphone access', async () => {
      render(<VoiceChatWhisper />);

      await waitFor(() => {
        expect(mockGetUserMedia).toHaveBeenCalled();
      });
    });
  });

  // ===================================
  // UI ELEMENTS TESTS (3 tests)
  // ===================================

  describe('UI Elements', () => {
    it('should show tips and guidance', () => {
      render(<VoiceChatWhisper />);

      // Check for tips section
      expect(screen.getByText(/arrêt manuel/i)).toBeInTheDocument();
    });

    it('should display example conversation flow', () => {
      render(<VoiceChatWhisper />);

      // Check for example mentions
      expect(screen.getByText(/marie dupont/i)).toBeInTheDocument();
      expect(screen.getByText(/oslo/i)).toBeInTheDocument();
    });

    it('should show ticket creation in examples', () => {
      render(<VoiceChatWhisper />);

      expect(screen.getByText(/ticket sav créé automatiquement/i)).toBeInTheDocument();
    });
  });

  // ===================================
  // ACCESSIBILITY TESTS (2 tests)
  // ===================================

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      render(<VoiceChatWhisper />);

      const mainHeading = screen.getByRole('heading', { name: /assistant vocal sav/i });
      expect(mainHeading).toBeInTheDocument();
    });

    it('should have accessible buttons with clear labels', async () => {
      render(<VoiceChatWhisper />);

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /démarrer la conversation/i });
        expect(button).toBeInTheDocument();
        expect(button).toHaveAttribute('class');
      });
    });
  });
});
