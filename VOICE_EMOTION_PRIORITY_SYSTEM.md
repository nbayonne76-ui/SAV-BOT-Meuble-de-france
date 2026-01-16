# 🎙️ Voice Emotion Priority System

## 📋 Overview

This system automatically analyzes customer voice conversations to detect emotional state and assigns ticket priority accordingly. Angry or frustrated customers get immediate attention (< 1h response), while calm customers follow normal prioritization (< 24h response).

## 🎯 Objective

Improve customer service response times based on emotional state:
- **Angry Client** → Response in < 1h (Priority P0/4)
- **Irritated Client** → Response in < 2h (Priority P1/3)
- **Desperate Client** → Response in < 4h (Priority P2/2)
- **Sad Client** → Response in < 8h (Priority P2/2)
- **Calm Client** → Response in < 24h (Priority P3/1)

## 🤖 Technologies

- **Claude API (Anthropic)** - Voice emotion analysis
- **OpenAI Whisper** - Voice transcription
- **GPT-4** - Emotion detection from text
- **FastAPI** - Backend API
- **PostgreSQL** - Ticket storage with emotion metadata

## 📊 Emotion to Priority Mapping

| Emotion | Icon | Priority | Urgency | Response Time | Description |
|---------|------|----------|---------|---------------|-------------|
| Fâché (Angry) | 🔴 | P0 (4) | URGENT | < 1h | Client très mécontent - Action immédiate |
| Énervé (Irritated) | 🟠 | P1 (3) | HIGH | < 2h | Client irrité - Réponse rapide |
| Désespéré (Desperate) | 🟡 | P2 (2) | MEDIUM | < 4h | Client découragé - Traitement prioritaire |
| Triste (Sad) | 🔵 | P2 (2) | MEDIUM | < 8h | Client déçu - Traitement standard |
| Calme (Calm) | 🟢 | P3 (1) | LOW | < 24h | Client serein - Traitement normal |

## 🏗️ Architecture

### Components

1. **VoiceEmotionDetector Service** (`app/services/voice_emotion_detector.py`)
   - Analyzes transcribed text for emotional indicators
   - Uses both keyword matching and AI analysis
   - Combines results with weighted average (AI: 70%, Keywords: 30%)

2. **Voice API Endpoints** (`app/api/endpoints/voice.py`)
   - `/transcribe` - Convert audio to text with Whisper
   - `/chat` - Process conversation with emotion analysis
   - `/speak` - Convert text response to speech
   - `/create-ticket` - Create SAV ticket with emotion-based priority

3. **Database Model** (`app/models/ticket.py`)
   - New fields: `voice_emotion`, `voice_emotion_confidence`, `voice_emotion_indicators`
   - Stores emotional context for each ticket

## 💻 Usage

### API Flow

1. **Client sends voice message**
   ```bash
   POST /api/voice/transcribe
   - Input: Audio file (mp3, wav, webm)
   - Output: Transcribed text
   ```

2. **Process conversation with emotion detection**
   ```bash
   POST /api/voice/chat
   {
     "message": "Transcribed text",
     "conversation_history": [...],
     "photos": []
   }
   ```

   Response includes:
   ```json
   {
     "response": "Bot response",
     "session_id": "session-123",
     "action": "recap|create_ticket|null",
     "ticket_data": {...},
     "emotion_analysis": {
       "emotion": "fache",
       "confidence": 0.92,
       "indicators": ["Utilisation de mots agressifs", "..."],
       "priority": "P0",
       "urgency": "urgent",
       "sla_hours": 1
     }
   }
   ```

3. **Create ticket with emotion-based priority**
   ```bash
   POST /api/voice/create-ticket
   {
     "customer_name": "John Doe",
     "problem_description": "...",
     "product": "Canapé",
     "order_number": "CMD-2025-12345",
     "photos": [...],
     "emotion_analysis": {...}
   }
   ```

## 🔧 Configuration

### Environment Variables

No additional configuration needed beyond existing OpenAI API key:
```env
OPENAI_API_KEY=sk-...
```

### Emotion Detection Thresholds

Configured in `voice_emotion_detector.py`:
- Minimum confidence: 0.3 (keyword-only)
- Maximum confidence: 0.95 (keyword + AI agreement)
- AI weight: 70%
- Keyword weight: 30%

## 🧠 How Emotion Detection Works

### 1. Keyword Analysis
Scans transcript for emotion-specific keywords:
- **Angry**: "inacceptable", "scandale", "honte", "furieux", "colère"
- **Irritated**: "agacé", "énervé", "frustré", "contrarié"
- **Desperate**: "désespéré", "ne sais plus quoi faire", "au bout du rouleau"
- **Sad**: "triste", "peine", "déçu", "navré"
- **Calm**: "comprends", "merci", "patient", "d'accord"

### 2. AI Analysis
GPT-4 analyzes the full context:
- Conversation history (last 3 messages)
- Current message transcript
- Tone indicators (aggression, politeness, etc.)
- Linguistic patterns (short/abrupt phrases, repetitions)

### 3. Combined Result
- If keyword and AI agree: High confidence (up to 95%)
- If they disagree: Trust AI but reduce confidence by 20%
- Final result: Weighted average of both analyses

## 📡 Integration with Existing SAV Workflow

The emotion system seamlessly integrates with the existing ticket creation process:

1. **Voice conversation flows normally** through chat endpoint
2. **Emotion is analyzed** in parallel with bot response
3. **When ticket is created**, emotion-based priority overrides default priority
4. **Ticket includes**:
   - Detected emotion
   - Confidence score
   - Indicators that led to detection
   - Note explaining the priority assignment

## 🗄️ Database Schema

New columns added to `sav_tickets` table:

```sql
ALTER TABLE sav_tickets
ADD COLUMN voice_emotion VARCHAR(50),           -- fache, enerve, desespere, triste, calme
ADD COLUMN voice_emotion_confidence FLOAT,      -- 0.0 to 1.0
ADD COLUMN voice_emotion_indicators JSONB;      -- ["indicator 1", "indicator 2", ...]
```

### Migration

Run the migration script to add emotion fields:

```bash
# Local database
cd backend
python migrate_add_voice_emotion.py

# Railway database (replace with your DB URL)
python migrate_railway_direct.py "postgresql://..."
```

## 📈 Analytics & Monitoring

### Metrics Collected

All emotion data is stored in the database for analytics:
- Number of tickets by emotion
- Average confidence scores
- Priority distribution
- Response time by emotion/priority
- Emotion trends over time

### Example Queries

```sql
-- Tickets by emotion
SELECT voice_emotion, COUNT(*) as count
FROM sav_tickets
WHERE voice_emotion IS NOT NULL
GROUP BY voice_emotion
ORDER BY count DESC;

-- Average confidence by emotion
SELECT voice_emotion, AVG(voice_emotion_confidence) as avg_confidence
FROM sav_tickets
WHERE voice_emotion IS NOT NULL
GROUP BY voice_emotion;

-- High-priority emotion tickets
SELECT ticket_id, voice_emotion, voice_emotion_confidence, priority
FROM sav_tickets
WHERE voice_emotion IN ('fache', 'enerve')
ORDER BY created_at DESC
LIMIT 10;
```

## 🔒 Privacy & Security

- **Audio files never stored** on server (processed in memory only)
- **Transcriptions temporary** (not persisted beyond session)
- **Emotion analysis results** stored for quality improvement
- **GDPR compliant** - emotion data can be deleted with ticket

## 🐛 Troubleshooting

### Low Confidence Scores

**Causes**:
- Poor audio quality (background noise)
- Unclear speech or mixed emotions
- Short messages without context

**Solution**: Encourage longer, clearer voice messages

### Incorrect Emotion Detection

**Causes**:
- Sarcasm or irony (hard for AI to detect)
- Cultural/linguistic nuances
- Keywords from previous context

**Solution**: Review indicators and adjust keyword lists if needed

### API Errors

```python
# If emotion detection fails, system falls back to:
{
  "emotion": "calme",
  "confidence": 0.5,
  "priority": "P3",
  "indicators": ["Analyse par défaut (erreur)"]
}
```

This ensures tickets are always created even if emotion analysis fails.

## 🧪 Testing

### Test with Sample Phrases

**Angry customer**:
> "C'est inadmissible ! Mon canapé est complètement cassé et personne ne répond ! Je suis furieux !"

Expected: `emotion: "fache"`, `priority: "P0"`, `confidence > 0.8`

**Calm customer**:
> "Bonjour, j'ai un petit problème avec ma table. Pas urgent, mais j'aimerais bien avoir votre avis. Merci."

Expected: `emotion: "calme"`, `priority: "P3"`, `confidence > 0.7`

### API Testing

```bash
# Test emotion detection
curl -X POST http://localhost:8000/api/voice/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Je suis vraiment énervé ! Mon meuble est arrivé cassé !",
    "conversation_history": []
  }'
```

## 📚 Code Examples

### Using the Emotion Detector

```python
from app.services.voice_emotion_detector import get_voice_emotion_detector

detector = get_voice_emotion_detector()

result = await detector.analyze_emotion(
    transcript="Je suis furieux ! C'est inacceptable !",
    conversation_history=[]
)

print(f"Emotion: {result['emotion']}")  # "fache"
print(f"Priority: {result['priority']}")  # "P0"
print(f"Confidence: {result['confidence']:.2f}")  # 0.92
```

### Frontend Integration

```javascript
// Send voice message with automatic emotion detection
const response = await fetch('/api/voice/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: transcribedText,
    conversation_history: history,
    photos: uploadedPhotos
  })
});

const data = await response.json();

// Display emotion to agent (not to customer)
if (data.emotion_analysis) {
  console.log(`🎯 Emotion detected: ${data.emotion_analysis.emotion}`);
  console.log(`Priority assigned: ${data.emotion_analysis.priority}`);

  // Show visual indicator to agent
  showEmotionIndicator(data.emotion_analysis);
}
```

## 🎉 Summary

You now have a complete voice emotion priority system that:
- ✅ Automatically analyzes customer emotional state
- ✅ Assigns appropriate ticket priority based on emotion
- ✅ Provides transparent indicators for why priority was assigned
- ✅ Integrates seamlessly with existing SAV workflow
- ✅ Stores emotion data for analytics and improvement
- ✅ Falls back gracefully if detection fails

## 🤝 Support

For questions or issues:
- Check logs in `/api/voice/` endpoints for emotion analysis results
- Review emotion indicators in ticket notes
- Adjust confidence thresholds in `voice_emotion_detector.py` if needed

## 📝 Changelog

### v1.0.0 (2026-01-16)
- Initial implementation of voice emotion detection
- Integrated with existing SAV workflow
- Added database fields for emotion metadata
- Created comprehensive documentation
