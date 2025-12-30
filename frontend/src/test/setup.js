import { afterEach, beforeAll, afterAll, vi } from 'vitest';
import { cleanup, configure } from '@testing-library/react';
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Configure Testing Library with higher timeouts for async operations
configure({
  asyncUtilTimeout: 5000, // Increase waitFor timeout from 1000ms to 5000ms
  getElementError: (message) => {
    const error = new Error(message);
    error.name = 'TestingLibraryElementError';
    return error;
  },
});

// Start MSW server before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'warn' });
});

// Reset handlers after each test
afterEach(() => {
  server.resetHandlers();
  cleanup();
});

// Close MSW server after all tests
afterAll(() => {
  server.close();
});

// Global test utilities
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock scrollIntoView (not available in jsdom)
Element.prototype.scrollIntoView = vi.fn();

// Mock crypto.randomUUID
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: () => 'test-uuid-' + Math.random().toString(36).substring(2, 9),
    subtle: {},
    getRandomValues: (arr) => arr
  },
  writable: true,
  configurable: true
});

// Mock Web Speech API
class MockSpeechRecognition {
  constructor() {
    this.continuous = false;
    this.interimResults = false;
    this.lang = 'fr-FR';
    this.onresult = null;
    this.onerror = null;
    this.onend = null;
    this.onstart = null;
  }
  start() {
    // Simulate async start event
    setTimeout(() => {
      if (this.onstart) {
        this.onstart();
      }
    }, 10);
  }
  stop() {
    // Simulate async stop event
    setTimeout(() => {
      if (this.onend) {
        this.onend();
      }
    }, 10);
  }
  abort() {
    if (this.onend) {
      this.onend();
    }
  }
}

global.SpeechRecognition = MockSpeechRecognition;
global.webkitSpeechRecognition = MockSpeechRecognition;

// Mock SpeechSynthesis API
const mockSpeechSynthesis = {
  speak: () => {},
  cancel: () => {},
  pause: () => {},
  resume: () => {},
  getVoices: () => [],
  speaking: false,
  pending: false,
  paused: false
};

global.speechSynthesis = mockSpeechSynthesis;
global.SpeechSynthesisUtterance = class {
  constructor(text) {
    this.text = text;
    this.lang = 'fr-FR';
    this.rate = 1;
    this.pitch = 1;
    this.volume = 1;
  }
};

// Mock AudioContext for Web Audio API
class MockAudioContext {
  constructor() {
    this.destination = {};
    this.sampleRate = 44100;
    this.currentTime = 0;
    this.state = 'running';
    this.onstatechange = null;
  }

  createMediaStreamSource() {
    return {
      connect: vi.fn(),
      disconnect: vi.fn()
    };
  }

  createAnalyser() {
    return {
      connect: vi.fn(),
      disconnect: vi.fn(),
      fftSize: 2048,
      frequencyBinCount: 1024,
      getByteTimeDomainData: vi.fn(),
      getByteFrequencyData: vi.fn()
    };
  }

  createGain() {
    return {
      connect: vi.fn(),
      disconnect: vi.fn(),
      gain: { value: 1 }
    };
  }

  createOscillator() {
    return {
      connect: vi.fn(),
      disconnect: vi.fn(),
      start: vi.fn(),
      stop: vi.fn(),
      frequency: { value: 440 }
    };
  }

  close() {
    return Promise.resolve();
  }

  resume() {
    return Promise.resolve();
  }

  suspend() {
    return Promise.resolve();
  }
}

// Ensure AudioContext is properly defined as a constructor
Object.defineProperty(global, 'AudioContext', {
  value: MockAudioContext,
  writable: true,
  configurable: true
});

Object.defineProperty(global, 'webkitAudioContext', {
  value: MockAudioContext,
  writable: true,
  configurable: true
});

// Also set on window explicitly for compatibility
if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'AudioContext', {
    value: MockAudioContext,
    writable: true,
    configurable: true
  });

  Object.defineProperty(window, 'webkitAudioContext', {
    value: MockAudioContext,
    writable: true,
    configurable: true
  });
}

// Mock MediaRecorder
class MockMediaRecorder {
  constructor() {
    this.state = 'inactive';
    this.ondataavailable = null;
    this.onstop = null;
    this.onerror = null;
  }

  start() {
    this.state = 'recording';
  }

  stop() {
    this.state = 'inactive';
    if (this.onstop) this.onstop();
  }

  pause() {
    this.state = 'paused';
  }

  resume() {
    this.state = 'recording';
  }
}

global.MediaRecorder = MockMediaRecorder;
global.MediaRecorder.isTypeSupported = () => true;

// Mock navigator.mediaDevices
Object.defineProperty(global.navigator, 'mediaDevices', {
  value: {
    getUserMedia: vi.fn().mockResolvedValue({
      getTracks: () => [],
      getAudioTracks: () => [],
      getVideoTracks: () => [],
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    }),
    enumerateDevices: vi.fn().mockResolvedValue([])
  },
  writable: true,
  configurable: true
});

// Mock FileReader for file upload tests
class MockFileReader {
  constructor() {
    this.result = null;
    this.error = null;
    this.readyState = 0; // EMPTY
    this.onload = null;
    this.onerror = null;
    this.onprogress = null;
    this.onloadstart = null;
    this.onloadend = null;
  }

  readAsDataURL(file) {
    this.readyState = 1; // LOADING
    if (this.onloadstart) this.onloadstart();

    // Simulate async file reading
    setTimeout(() => {
      this.readyState = 2; // DONE
      // Create a fake base64 data URL based on file type
      const fileType = file.type || 'application/octet-stream';
      this.result = `data:${fileType};base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==`;

      if (this.onload) {
        this.onload({ target: { result: this.result } });
      }
      if (this.onloadend) this.onloadend();
    }, 10);
  }

  readAsText(file) {
    this.readyState = 1; // LOADING
    if (this.onloadstart) this.onloadstart();

    setTimeout(() => {
      this.readyState = 2; // DONE
      this.result = 'mock file content';

      if (this.onload) {
        this.onload({ target: { result: this.result } });
      }
      if (this.onloadend) this.onloadend();
    }, 10);
  }

  readAsArrayBuffer(file) {
    this.readyState = 1; // LOADING
    if (this.onloadstart) this.onloadstart();

    setTimeout(() => {
      this.readyState = 2; // DONE
      this.result = new ArrayBuffer(8);

      if (this.onload) {
        this.onload({ target: { result: this.result } });
      }
      if (this.onloadend) this.onloadend();
    }, 10);
  }

  abort() {
    this.readyState = 2; // DONE
  }
}

// Constants for FileReader states
MockFileReader.EMPTY = 0;
MockFileReader.LOADING = 1;
MockFileReader.DONE = 2;

global.FileReader = MockFileReader;

// Mock URL.createObjectURL and revokeObjectURL for file previews
const blobUrls = new Map();
let blobUrlCounter = 0;

global.URL.createObjectURL = vi.fn((blob) => {
  const url = `blob:http://localhost:5173/mock-blob-${blobUrlCounter++}`;
  blobUrls.set(url, blob);
  return url;
});

global.URL.revokeObjectURL = vi.fn((url) => {
  blobUrls.delete(url);
});

// Mock Blob if not available
if (typeof global.Blob === 'undefined') {
  global.Blob = class Blob {
    constructor(parts = [], options = {}) {
      this.size = parts.reduce((acc, part) => acc + (part.length || 0), 0);
      this.type = options.type || '';
      this.parts = parts;
    }

    slice(start = 0, end = this.size, contentType = '') {
      return new Blob(this.parts.slice(start, end), { type: contentType });
    }

    async text() {
      return this.parts.join('');
    }

    async arrayBuffer() {
      return new ArrayBuffer(this.size);
    }
  };
}

// Mock File if not available
if (typeof global.File === 'undefined') {
  global.File = class File extends global.Blob {
    constructor(parts, name, options = {}) {
      super(parts, options);
      this.name = name;
      this.lastModified = options.lastModified || Date.now();
    }
  };
}
