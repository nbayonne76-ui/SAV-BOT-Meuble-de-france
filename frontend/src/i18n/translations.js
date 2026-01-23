const supportedLanguages = {
  fr: { label: "Français", locale: "fr-FR", short: "fr" },
  en: { label: "English", locale: "en-US", short: "en" },
  ar: { label: "العربية", locale: "ar-SA", short: "ar" },
};

const translations = {
  fr: {
    chat: {
      welcome: {
        long: `Bonjour et bienvenue au service clientèle du groupe Mobilier de France.\nNous sommes à votre écoute pour un accompagnement personnalisé.\n\nPour vous aider rapidement, donnez-moi :\n• Votre numéro de commande ⭐ (prioritaire)\n• Votre nom\n• Une description de votre problème\n\nVous pouvez écrire ou utiliser le microphone 🎤`,
        short:
          "Bonjour et bienvenue au service clientèle du groupe Mobilier de France. Nous sommes à votre écoute pour un accompagnement personnalisé. Pour vous aider rapidement, donnez-moi votre numéro de commande (prioritaire), votre nom, et une description de votre problème.",
      },
      voice_on: "Voix ON",
      voice_off: "Voix OFF",
      voice_title_on: "Désactiver la voix du bot",
      voice_title_off: "Activer la voix du bot",
      language_label: "Langue",
      voice_mode_hint: "🎤 Parler au lieu de taper",
      validate_prompt: "⚡ Ces informations sont-elles correctes ?",
      btn_validate: "✅ Valider",
      btn_modify: "✏️ Modifier",
      validate_hint:
        'Cliquez sur "Valider" pour créer votre ticket, ou "Modifier" pour corriger les informations',
      subtitle:
        "Service d'Accompagnement Intelligent • Traitement automatisé en temps réel",
      automation_title: "🎯 100% Automatisé",
      automation_features: "✅ Analyse TON • ✅ Garantie • ✅ Priorité",
      file_video_label: "📹 Vidéo",
      upload_type_not_supported: "Type de fichier non supporté: {name}",
      upload_file_too_large: "Fichier trop volumineux: {name} (max {max}MB)",
      alert_microphone_denied:
        "🚫 Accès au microphone refusé.\n\nVeuillez autoriser l'accès dans les paramètres de votre navigateur.",
      alert_network: "🌐 Erreur réseau. Vérifiez votre connexion internet.",
      stt_not_available:
        "⚠️ Reconnaissance vocale non disponible\n\nUtilisez Chrome ou Edge pour cette fonctionnalité.",
      error_general:
        "Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ?",
      btn_yes: "Oui",
      btn_no: "Non",
      delete: "Supprimer",
      header_title: "Assistant Vocal d'Accompagnement - Mode Conversationnel",
      header_subtitle:
        "BB Expansion Mobilier de France - Clientèle groupe à votre écoute",
      mic_allowed: "Microphone autorisé - Prêt à démarrer",
      mic_blocked:
        "Microphone bloqué - Veuillez autoriser l'accès dans les paramètres du navigateur",
      mic_checking: "Vérification du microphone...",
      start_button_start: "Démarrer la Conversation",
      start_button_not_allowed: "Microphone non autorisé",
      start_helper_granted:
        "Cliquez pour commencer • L'enregistrement démarre automatiquement",
      start_helper_denied: "Autorisez le microphone pour continuer",
      start_helper_checking: "Autorisation du microphone en cours...",
      add_photos: "Ajouter Photos",
      photos_uploaded: "Photos uploadées ({count})",
      tips_title: "Conseils pour une conversation réussie",
      tips_speak_clearly: "Parlez clairement",
      tips_wait_response: "Attendez la réponse",
      tips_speak_naturally: "Parlez naturellement",
      tips_manual_stop: "Arrêt manuel",
      tips_speak_clearly_desc: "Articulez bien, pas trop vite",
      tips_wait_response_desc: "Patientez 1-2 secondes entre chaque échange",
      tips_speak_naturally_desc: "Vous pouvez tout dire en une fois",
      example_title: "Exemple de conversation",
      example_bot: "Bot:",
      example_user: "Vous:",
      example_bot_greeting: "Bonjour ! Quel est votre nom ?",
      example_user_input:
        "Marie Dupont, mon canapé OSLO CMD-2024-12345 a un pied cassé",
      example_bot_recap: "récapitulatif complet",
      example_user_confirm: "Oui",
      user_label: "👤 Vous",
      assistant_label: "🤖 Assistant",
      recording_label: "Enregistrement...",
      stop_button: "Arrêter",
      recording_help: 'Parlez puis cliquez sur "Arrêter" • Limite: 30 secondes',
      speaking_label: "Je parle...",
      end_conversation: "Terminer la Conversation",
      confirm_ticket_success:
        "Parfait ! Votre demande d'accompagnement a été créée avec succès. Vous pouvez la consulter dans le tableau de bord.",
      cancel_restart: "D'accord, recommençons. Décrivez-moi votre problème.",
      auto_ticket_created:
        "✅ Demande d'accompagnement créée automatiquement !",
      recap_label: "Récapitulatif",
      recap_trigger: "Je récapitule",
      ticket_created: "✅ Ticket créé !",

      creating_ticket: "Création de la demande d'accompagnement...",
      upload_error: "Erreur lors de l'upload des fichiers",
      error_ticket_validation:
        "Erreur lors de la validation du ticket. Veuillez réessayer.",
      error_ticket_cancel:
        "Erreur lors de l'annulation du ticket. Veuillez réessayer.",
      error_ticket_creation:
        "Erreur lors de la création du ticket. Veuillez réessayer.",
      listening: "🎤 Écoute en cours...",
      transcription_live_label: "Transcription en direct:",
      speak_now: "Parlez maintenant... Le texte apparaîtra ici en temps réel",
      files_to_send: "📎 Fichiers à envoyer ({count}):",
      header_main_title: "🛠️ Mobilier de France - Accompagnement",
      automation_label: "🎯 100% Automatisé",
      automation_items: "✅ Analyse TON • ✅ Garantie • ✅ Priorité",
      voice_speaking_suffix: "(parle...)",
      welcome_message_reset: `Bonjour et bienvenue au service clientèle du groupe Mobilier de France.
Nous sommes à votre écoute pour un accompagnement personnalisé.

Pour vous aider rapidement, donnez-moi :
• Votre numéro de commande ⭐ (prioritaire)
• Votre nom
• Une description de votre problème

Vous pouvez écrire ou utiliser le microphone 🎤`,
      placeholder:
        "Nom complet + Problème + N° commande... (Ex: Jean Dupont, mon canapé OSLO a un pied cassé, CMD-2024-12345)",
      info_secure:
        "🔒 Données sécurisées • ⚡ Réponse immédiate • 🎤 Conversation vocale complète • 🔊 Le bot vous parle • 🎯 Analyse automatique du TON et PRIORITÉ • 🛡️ Vérification garantie instantanée",
      bot_speaking: "🔊 Le bot est en train de parler... Écoutez sa réponse",
      video_label: "📹 Vidéo",
      error_mic_alert:
        "⚠️ Reconnaissance vocale non disponible\n\nUtilisez Chrome ou Edge pour cette fonctionnalité.",
      error_mic_already_running:
        "Impossible de démarrer le microphone. Rechargez la page.",
      error_mic_not_allowed:
        "❌ Erreur microphone\n\nVérifiez que le microphone est autorisé dans votre navigateur.",
      error_problem:
        "Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ?",
    },
    dashboard: {
      title: "📊 Tableau de Bord - Accompagnement",
      subtitle:
        "Gestion centralisée des demandes de la clientèle groupe Mobilier de France",
      refresh: "Actualiser",
      retry: "Réessayer",
      error_connection: "Erreur de connexion",
      loading: "Chargement des demandes d'accompagnement...",
      no_tickets: "Aucune demande trouvée",
      no_tickets_hint:
        "Créez votre première demande via le Bot Accompagnement (Texte) ou le Mode Vocal",
      view_dossier: "Voir le dossier",
      error_loading_dossier: "Erreur lors du chargement du dossier",
      download_json: "Télécharger JSON",
      close: "Fermer",
      dossier_title: "Dossier Clientèle",
      stats: {
        total_label: "Total Tickets",
        p0_label: "Critiques (P0)",
        p1_label: "Urgents (P1)",
        auto_resolved: "Auto-résolus",
      },
      columns: {
        ticket: "Ticket",
        client: "Client",
        issue: "Problème",
        priority: "Priorité",
        tone: "Ton",
        status: "Statut",
        date: "Date",
        actions: "Actions",
      },
      status_labels: {
        escalated_to_human: "Escaladé",
        awaiting_technician: "En attente technicien",
        auto_resolved: "Résolu auto",
        evidence_collection: "Collecte preuves",
        pending: "En attente",
      },
      refresh: "Actualiser",
      filters: {
        priority: "Priorité:",
        status: "Statut:",
        all: "Tous",
        all_priority: "Toutes",
        p0_critical: "P0 - Critique",
        p1_urgent: "P1 - Urgent",
        p2_moderate: "P2 - Modéré",
        p3_low: "P3 - Faible",
        escalated: "Escaladés",
        awaiting_tech: "En attente technicien",
        auto_resolved_filter: "Auto-résolus",
        evidence_collection_filter: "Collecte preuves",
      },
    },
    nav: {
      chat: "Bot Accompagnement (Texte)",
      voice: "Mode Vocal",
      dashboard: "Tableau de Bord",
    },
    voice: {
      processing: {
        transcription: "Transcription en cours...",
        generating: "Génération de la réponse...",
        summary_synthesis: "Synthèse vocale du récapitulatif...",
        synthesis: "Synthèse vocale...",
        recording_too_short: "Enregistrement trop court, redémarrage...",
      },
      error_transcription: "Erreur de transcription",
      error_tts: "Erreur de synthèse vocale",
    },
  },
  en: {
    chat: {
      welcome: {
        long: `Hello and welcome to Mobilier de France customer support. We are here to help you.\n\nTo assist quickly, please provide:\n• Your order number ⭐ (priority)\n• Your name\n• A description of your issue\n\nYou can type or use the microphone 🎤`,
        short:
          "Hello and welcome to Mobilier de France customer support. Please provide your order number (priority), your name, and issue description.",
      },
      voice_on: "Voice ON",
      voice_off: "Voice OFF",
      voice_title_on: "Disable bot voice",
      voice_title_off: "Enable bot voice",
      language_label: "Language",
      validate_prompt: "⚡ Is this information correct?",
      btn_validate: "✅ Confirm",
      btn_modify: "✏️ Edit",
      validate_hint:
        "Click the button to confirm (or modify) — localized string",
      subtitle: "Intelligent Support • Automated handling in real-time",
      automation_title: "🎯 Fully automated",
      automation_features: "✅ Tone analysis • ✅ Warranty • ✅ Priority",
      file_video_label: "📹 Video",
      upload_type_not_supported: "File type not supported: {name}",
      upload_file_too_large: "File too large: {name} (max {max}MB)",
      alert_microphone_denied:
        "🚫 Microphone access denied.\n\nPlease enable access in your browser settings.",
      alert_network: "🌐 Network error. Check your internet connection.",
      stt_not_available:
        "⚠️ Speech recognition not available\n\nUse Chrome or Edge for this feature.",
      error_general:
        "Sorry — I encountered a technical problem. Can you try again?",
      btn_yes: "Yes",
      btn_no: "No",
      delete: "Delete",
      header_title: "Voice Assistant - Conversational Mode",
      header_subtitle:
        "BB Expansion Mobilier de France - Group customer support",
      mic_allowed: "Microphone allowed - Ready to start",
      mic_blocked:
        "Microphone blocked - Please enable access in browser settings",
      mic_checking: "Checking microphone...",
      start_button_start: "Start Conversation",
      start_button_not_allowed: "Microphone not allowed",
      start_helper_granted: "Click to start • Recording starts automatically",
      start_helper_denied: "Enable the microphone to continue",
      start_helper_checking: "Microphone permission in progress...",
      add_photos: "Add Photos",
      photos_uploaded: "Uploaded photos ({count})",
      tips_title: "Tips for a successful conversation",
      tips_speak_clearly: "Speak clearly",
      tips_wait_response: "Wait for the response",
      tips_speak_naturally: "Speak naturally",
      tips_manual_stop: "Manual stop",
      tips_speak_clearly_desc: "Articulate clearly, not too fast",
      tips_wait_response_desc: "Wait 1-2 seconds between exchanges",
      tips_speak_naturally_desc: "You can say everything in one go",
      example_title: "Conversation example",
      example_bot: "Bot:",
      example_user: "You:",
      example_bot_greeting: "Hello! What is your name?",
      example_user_input:
        "John Smith, my OSLO sofa CMD-2024-12345 has a broken leg",
      example_bot_recap: "complete summary",
      example_user_confirm: "Yes",
      user_label: "👤 You",
      assistant_label: "🤖 Assistant",
      recording_label: "Recording...",
      stop_button: "Stop",
      recording_help: 'Speak then click "Stop" • Limit: 30 seconds',
      speaking_label: "I'm speaking...",
      end_conversation: "End Conversation",
      confirm_ticket_success:
        "Great! Your support request was created successfully. You can view it in the dashboard.",
      cancel_restart: "Okay, let's start over. Please describe your issue.",
      creating_ticket: "Creating support request...",
      upload_error: "Error uploading files",
      auto_ticket_created: "✅ Support request created automatically!",
      recap_label: "Summary",
      recap_trigger: "I summarize",
      ticket_created: "✅ Ticket created!",
      error_ticket_validation: "Error validating the ticket. Please try again.",
      error_ticket_cancel: "Error cancelling the ticket. Please try again.",
      error_ticket_creation: "Error creating the ticket. Please try again.",
      listening: "🎤 Listening...",
      transcription_live_label: "Live transcription:",
      speak_now: "Speak now... text will appear here in real time",
      files_to_send: "📎 Files to send ({count}):",
      header_main_title: "🛠️ Mobilier de France - Support",
      automation_label: "🎯 Fully automated",
      automation_items: "✅ Tone analysis • ✅ Warranty • ✅ Priority",
      voice_speaking_suffix: "(speaking...)",
      welcome_message_reset: `Hello and welcome to Mobilier de France customer support. We are here to help you.

To assist quickly, please provide:
• Your order number ⭐ (priority)
• Your name
• A description of your issue

You can type or use the microphone 🎤`,
      placeholder:
        "Full name + Issue + Order number... (Ex: John Smith, my OSLO sofa has a broken leg, CMD-2024-12345)",
      info_secure:
        "🔒 Secure data • ⚡ Immediate response • 🎤 Full voice conversation • 🔊 Bot speaks • 🎯 Automatic tone and priority analysis • 🛡️ Instant warranty check",
      bot_speaking: "🔊 The bot is speaking... Listen to the response",
      video_label: "📹 Video",
      error_mic_alert:
        "⚠️ Speech recognition not available\n\nUse Chrome or Edge for this feature.",
      error_mic_already_running: "Unable to start microphone. Reload the page.",
      error_mic_not_allowed:
        "❌ Microphone error\n\nCheck that microphone is enabled in your browser.",
      error_problem:
        "Sorry, I encountered a technical problem. Can you try again?",
    },
    dashboard: {
      title: "📊 Dashboard - Support",
      subtitle:
        "Centralized management of Mobilier de France group customer requests",
      refresh: "Refresh",
      retry: "Retry",
      error_connection: "Connection error",
      loading: "Loading support requests...",
      no_tickets: "No requests found",
      no_tickets_hint:
        "Create your first request via the Chat (Text) or Voice Mode",
      view_dossier: "View dossier",
      error_loading_dossier: "Error loading dossier",
      download_json: "Download JSON",
      close: "Close",
      dossier_title: "Customer File",
      filters: {
        priority: "Priority:",
        status: "Status:",
        all: "All",
        all_priority: "All",
        p0_critical: "P0 - Critical",
        p1_urgent: "P1 - Urgent",
        p2_moderate: "P2 - Moderate",
        p3_low: "P3 - Low",
        escalated: "Escalated",
        awaiting_tech: "Awaiting technician",
        auto_resolved_filter: "Auto-resolved",
        evidence_collection_filter: "Evidence collection",
      },
    },
    nav: {
      chat: "Chat (Text)",
      voice: "Voice Mode",
      dashboard: "Dashboard",
    },
    voice: {
      processing: {
        transcription: "Transcription in progress...",
        generating: "Generating response...",
        summary_synthesis: "Synthesizing summary...",
        synthesis: "Synthesizing...",
        recording_too_short: "Recording too short, restarting...",
      },
      error_transcription: "Transcription error",
      error_tts: "Text-to-speech error",
    },
  },
  ar: {
    chat: {
      welcome: {
        long: `مرحبًا بك في خدمة عملاء مجموعة Mobilier de France. نحن هنا لمساعدتك.\n\nللمساعدة السريعة، يرجى تقديم:\n• رقم الطلب ⭐ (أولوية)\n• اسمك\n• وصف المشكلة\n\nيمكنك الكتابة أو استخدام الميكروفون 🎤`,
        short:
          "مرحبًا بك في خدمة عملاء Mobilier de France. الرجاء تقديم رقم الطلب (أولوية) واسمك ووصف المشكلة.",
      },
      voice_on: "الصوت مفعل",
      voice_off: "الصوت متوقف",
      voice_title_on: "إيقاف صوت البوت",
      voice_title_off: "تشغيل صوت البوت",
      language_label: "اللغة",
      validate_prompt: "⚡ هل هذه المعلومات صحيحة؟",
      btn_validate: "✅ تأكيد",
      btn_modify: "✏️ تعديل",
      validate_hint:
        'انقر على "تأكيد" لإنشاء التذكرة، أو "تعديل" لتصحيح المعلومات',
      subtitle: "خدمة دعم ذكية • معالجة تلقائية في الوقت الفعلي",
      automation_title: "🎯 مؤتمت 100%",
      automation_features: "✅ تحليل النبرة • ✅ الضمان • ✅ الأولوية",
      file_video_label: "📹 فيديو",
      upload_type_not_supported: "نوع الملف غير مدعوم: {name}",
      upload_file_too_large: "الملف كبير جدًا: {name} (الحد {max}MB)",
      alert_microphone_denied:
        "🚫 تم رفض الوصول إلى الميكروفون.\n\nيرجى تمكين الوصول في إعدادات المتصفح.",
      alert_network: "🌐 خطأ في الشبكة. تحقق من اتصال الإنترنت الخاص بك.",
      error_general: "عذرًا، حدثت مشكلة فنية. هل يمكنك المحاولة مرة أخرى؟",
      btn_yes: "نعم",
      btn_no: "لا",
      delete: "حذف",
      header_title: "المساعد الصوتي - وضع المحادثة",
      header_subtitle: "BB Expansion Mobilier de France - دعم العملاء للمجموعة",
      mic_allowed: "الميكروفون مفعل - جاهز للبدء",
      mic_blocked: "الميكروفون محظور - يرجى تمكين الوصول في إعدادات المتصفح",
      mic_checking: "جارٍ التحقق من الميكروفون...",
      start_button_start: "بدء المحادثة",
      start_button_not_allowed: "الميكروفون غير مفعل",
      start_helper_granted: "انقر للبدء • يبدأ التسجيل تلقائيًا",
      start_helper_denied: "قم بتمكين الميكروفون للمتابعة",
      start_helper_checking: "جاري طلب إذن الميكروفون...",
      add_photos: "إضافة صور",
      photos_uploaded: "الصور المرفوعة ({count})",
      tips_title: "نصائح لمحادثة ناجحة",
      tips_speak_clearly: "تحدث بوضوح",
      tips_wait_response: "انتظر الرد",
      tips_speak_naturally: "تحدث بشكل طبيعي",
      tips_manual_stop: "إيقاف يدوي",
      tips_speak_clearly_desc: "تحدث بوضوح، ليس بسرعة كبيرة",
      tips_wait_response_desc: "انتظر 1-2 ثانية بين كل تبادل",
      tips_speak_naturally_desc: "يمكنك قول كل شيء مرة واحدة",
      example_title: "مثال للمحادثة",
      example_bot: "البوت:",
      example_user: "أنت:",
      example_bot_greeting: "مرحبا! ما اسمك؟",
      example_user_input: "أحمد محمد، كنبتي OSLO CMD-2024-12345 بها رجل مكسورة",
      example_bot_recap: "ملخص كامل",
      example_user_confirm: "نعم",
      user_label: "👤 أنت",
      assistant_label: "🤖 المساعد",
      recording_label: "جارٍ التسجيل...",
      stop_button: "إيقاف",
      recording_help: 'تحدث ثم انقر "إيقاف" • الحد: 30 ثانية',
      speaking_label: "أتحدث...",
      end_conversation: "إنهاء المحادثة",
      confirm_ticket_success:
        "رائع! تم إنشاء طلب الدعم بنجاح. يمكنك عرضه في لوحة التحكم.",
      cancel_restart: "حسنًا، لنبدأ من جديد. الرجاء وصف مشكلتك.",
      creating_ticket: "جاري إنشاء طلب الدعم...",
      upload_error: "خطأ أثناء رفع الملفات",
      auto_ticket_created: "✅ تم إنشاء طلب الدعم تلقائيًا!",
      recap_label: "ملخص",
      recap_trigger: "سأقوم بالتلخيص",
      ticket_created: "✅ تم إنشاء التذكرة!",
      error_ticket_validation:
        "حدث خطأ أثناء تأكيد التذكرة. الرجاء المحاولة مرة أخرى.",
      error_ticket_cancel:
        "حدث خطأ أثناء إلغاء التذكرة. الرجاء المحاولة مرة أخرى.",
      error_ticket_creation:
        "حدث خطأ أثناء إنشاء التذكرة. الرجاء المحاولة مرة أخرى.",
      listening: "🎤 جارٍ الاستماع...",
      transcription_live_label: "النص الحي:",
      speak_now: "تحدث الآن... سيظهر النص هنا في الوقت الفعلي",
      files_to_send: "📎 الملفات المراد إرسالها ({count}):",
      header_main_title: "🛠️ Mobilier de France - الدعم",
      automation_label: "🎯 مؤتمت 100%",
      automation_items: "✅ تحليل النبرة • ✅ الضمان • ✅ الأولوية",
      voice_speaking_suffix: "(يتحدث...)",
      welcome_message_reset: `مرحبًا بك في خدمة عملاء مجموعة Mobilier de France. نحن هنا لمساعدتك.

للمساعدة السريعة، يرجى تقديم:
• رقم الطلب ⭐ (أولوية)
• اسمك
• وصف المشكلة

يمكنك الكتابة أو استخدام الميكروفون 🎤`,
      placeholder:
        "الاسم الكامل + المشكلة + رقم الطلب... (مثال: أحمد محمد، كنبتي OSLO بها رجل مكسورة، CMD-2024-12345)",
      info_secure:
        "🔒 بيانات آمنة • ⚡ رد فوري • 🎤 محادثة صوتية كاملة • 🔊 البوت يتحدث • 🎯 تحليل تلقائي للنبرة والأولوية • 🛡️ فحص الضمان الفوري",
      bot_speaking: "🔊 البوت يتحدث... استمع للرد",
      video_label: "📹 فيديو",
      error_mic_alert:
        "⚠️ التعرف على الكلام غير متاح\n\nاستخدم Chrome أو Edge لهذه الميزة.",
      error_mic_already_running: "لا يمكن بدء الميكروفون. أعد تحميل الصفحة.",
      error_mic_not_allowed:
        "❌ خطأ في الميكروفون\n\nتحقق من أن الميكروفون مفعل في متصفحك.",
      error_problem: "عذرًا، حدثت مشكلة فنية. هل يمكنك المحاولة مرة أخرى؟",
    },
    dashboard: {
      title: "📊 لوحة التحكم - الدعم",
      subtitle: "الإدارة المركزية لطلبات عملاء مجموعة Mobilier de France",
      refresh: "تحديث",
      retry: "أعد المحاولة",
      error_connection: "خطأ في الاتصال",
      loading: "جارٍ تحميل الطلبات...",
      no_tickets: "لم يتم العثور على طلبات",
      no_tickets_hint: "أنشئ طلبك الأول عبر بوت المحادثة (نص) أو الوضع الصوتي",
      view_dossier: "عرض الملف",
      error_loading_dossier: "حدث خطأ أثناء تحميل الملف",
      download_json: "تحميل JSON",
      close: "إغلاق",
      dossier_title: "ملف العميل",
      filters: {
        priority: "الأولوية:",
        status: "الحالة:",
        all: "الكل",
        all_priority: "الكل",
        p0_critical: "P0 - حرج",
        p1_urgent: "P1 - عاجل",
        p2_moderate: "P2 - متوسط",
        p3_low: "P3 - منخفض",
        escalated: "تم تصعيده",
        awaiting_tech: "في انتظار الفني",
        auto_resolved_filter: "تم حلها تلقائيًا",
        evidence_collection_filter: "جمع الأدلة",
      },
    },
    nav: {
      chat: "بوت (نص)",
      voice: "الوضع الصوتي",
      dashboard: "لوحة التحكم",
    },
    voice: {
      processing: {
        transcription: "جاري التفريغ...",
        generating: "يتم إنشاء الرد...",
        summary_synthesis: "يتم توليف الملخص صوتياً...",
        synthesis: "يتم التوليف الصوتي...",
        recording_too_short: "التسجيل قصير جدًا، إعادة التشغيل...",
      },
      error_transcription: "خطأ في التفريغ",
      error_tts: "خطأ في التوليف الصوتي",
    },
  },
};

export { supportedLanguages };
export default translations;
