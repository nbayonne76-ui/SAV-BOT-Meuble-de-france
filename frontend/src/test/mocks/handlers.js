import { http, HttpResponse, delay } from 'msw';

// Use relative paths for MSW handlers to work in tests
const API_URL = import.meta.env.VITE_API_URL || '';

// Helper to simulate network latency (helps with test synchronization)
const simulateNetworkDelay = () => delay(50); // 50ms delay

export const handlers = [
  // Chat endpoint
  http.post(`${API_URL}/api/chat`, async ({ request }) => {
    await simulateNetworkDelay();
    const body = await request.json();

    // Default success response
    return HttpResponse.json({
      response: 'Bonjour ! Je suis votre assistant SAV. Comment puis-je vous aider aujourd\'hui ?',
      session_id: body.session_id || 'test-session-123',
      requires_confirmation: false,
      ticket_data: null
    });
  }),

  // Create ticket endpoint
  http.post(`${API_URL}/api/chat/create-ticket`, async ({ request }) => {
    await simulateNetworkDelay();
    const body = await request.json();

    return HttpResponse.json({
      success: true,
      ticket_id: 'SAV-2024-TEST-001',
      message: 'Ticket créé avec succès'
    });
  }),

  // Upload endpoint
  http.post(`${API_URL}/api/upload`, async ({ request }) => {
    await simulateNetworkDelay();

    // Extract file names from the request
    const formData = await request.formData();
    const files = formData.getAll('files');

    const uploadedFiles = files.map((file, index) => ({
      original_name: file.name,
      saved_name: `20240115000${index}_${file.name}`,
      url: `/uploads/photos/20240115000${index}_${file.name}`,
      size: file.size,
      type: file.name.split('.').pop().toLowerCase()
    }));

    return HttpResponse.json({
      success: true,
      files: uploadedFiles,
      count: uploadedFiles.length
    });
  }),

  // Get tickets endpoint
  http.get(`${API_URL}/api/sav/tickets`, async () => {
    await simulateNetworkDelay();
    return HttpResponse.json({
      success: true,
      tickets: [
        {
          ticket_id: 1,
          numero_ticket: 'SAV-2024-001',
          nom_client: 'Jean Dupont',
          email: 'jean.dupont@example.com',
          telephone: '0612345678',
          produit: 'Canapé Luna',
          reference_produit: 'CAP-LUNA-001',
          probleme: 'Tissu déchiré',
          status: 'nouveau',
          priority: 'P0',
          tone: 'angry',
          date_creation: '2024-01-15T10:30:00Z',
          photos: [],
          auto_resolved: false
        },
        {
          ticket_id: 2,
          numero_ticket: 'SAV-2024-002',
          nom_client: 'Marie Martin',
          email: 'marie.martin@example.com',
          telephone: '0623456789',
          produit: 'Table Élégance',
          reference_produit: 'TAB-ELEG-001',
          probleme: 'Rayure sur le plateau',
          status: 'en_cours',
          priority: 'P1',
          tone: 'neutral',
          date_creation: '2024-01-16T14:20:00Z',
          photos: ['http://localhost:8000/uploads/table-rayure.jpg'],
          auto_resolved: false
        }
      ]
    });
  }),

  // Confirm ticket endpoint
  http.post(`${API_URL}/api/sav/tickets/:id/confirm`, async ({ params }) => {
    await simulateNetworkDelay();
    return HttpResponse.json({
      success: true,
      ticket_id: parseInt(params.id),
      numero_ticket: `SAV-2024-${params.id.toString().padStart(3, '0')}`,
      message: 'Ticket SAV créé avec succès'
    });
  }),

  // Cancel ticket endpoint
  http.post(`${API_URL}/api/sav/tickets/:id/cancel`, async ({ params }) => {
    await simulateNetworkDelay();
    return HttpResponse.json({
      success: true,
      ticket_id: parseInt(params.id),
      message: 'Ticket annulé'
    });
  })
];

// Specific handlers for different test scenarios
export const chatHandlers = {
  // Chat response with ticket creation
  withTicketConfirmation: http.post(`${API_URL}/api/chat`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      response: 'Parfait ! Je vais créer votre ticket SAV. Confirmez-vous les informations ?',
      session_id: body.session_id,
      requires_confirmation: true,
      ticket_data: {
        nom_client: 'Test User',
        email: 'test@example.com',
        telephone: '0612345678',
        produit: 'Canapé Test',
        reference_produit: 'CAP-TEST-001',
        probleme: 'Problème de test',
        priorite: 'haute'
      }
    });
  }),

  // Error response
  withError: http.post(`${API_URL}/api/chat`, () => {
    return HttpResponse.json(
      { error: 'Erreur de traitement du message' },
      { status: 500 }
    );
  }),

  // Network error
  withNetworkError: http.post(`${API_URL}/api/chat`, () => {
    return HttpResponse.error();
  })
};

export const uploadHandlers = {
  // Upload with multiple files
  withMultipleFiles: http.post(`${API_URL}/api/upload`, async () => {
    return HttpResponse.json({
      success: true,
      files: [
        {
          original_name: 'photo1.jpg',
          saved_name: '202401150001_photo1.jpg',
          url: '/uploads/photos/202401150001_photo1.jpg',
          size: 102400,
          type: 'jpg'
        },
        {
          original_name: 'photo2.jpg',
          saved_name: '202401150002_photo2.jpg',
          url: '/uploads/photos/202401150002_photo2.jpg',
          size: 204800,
          type: 'jpg'
        }
      ],
      count: 2
    });
  }),

  // Upload error
  withError: http.post(`${API_URL}/api/upload`, () => {
    return HttpResponse.json(
      { error: 'Erreur lors de l\'upload' },
      { status: 500 }
    );
  }),

  // File too large error
  withFileTooLarge: http.post(`${API_URL}/api/upload`, () => {
    return HttpResponse.json(
      { error: 'Fichier trop volumineux' },
      { status: 413 }
    );
  })
};

export const ticketHandlers = {
  // Empty tickets list
  withEmptyList: http.get(`${API_URL}/api/sav/tickets`, () => {
    return HttpResponse.json({ success: true, tickets: [] });
  }),

  // Tickets with error
  withError: http.get(`${API_URL}/api/sav/tickets`, () => {
    return HttpResponse.json(
      { success: false, error: 'Erreur lors de la récupération des tickets' },
      { status: 500 }
    );
  })
};
