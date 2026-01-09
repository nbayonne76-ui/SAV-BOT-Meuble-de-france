const supportedLanguages = {
  fr: { label: "Français", locale: "fr-FR", short: "fr" },
  en: { label: "English", locale: "en-US", short: "en" },
  ar: { label: "العربية", locale: "ar-SA", short: "ar" },
};

const translations = {
  fr: {
    chat: {
      welcome: {
        long: `Bonjour et bienvenue au service clientèle du groupe Mobilier de France.\nNous sommes à votre écoute pour un accompagnement personnalisé.\n\nPour vous aider rapidement, donnez-moi :\n• Votre nom\n• Votre numéro de commande\n• Une description de votre problème\n\nVous pouvez écrire ou utiliser le microphone 🎤`,
        short:
          "Bonjour et bienvenue au service clientèle du groupe Mobilier de France. Nous sommes à votre écoute pour un accompagnement personnalisé. Pour vous aider rapidement, donnez-moi votre nom, votre numéro de commande, et une description de votre problème.",
      },
      voice_on: "Voix ON",
      voice_off: "Voix OFF",
      voice_title_on: "Désactiver la voix du bot",
      voice_title_off: "Activer la voix du bot",
      language_label: "Langue",
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
    },
    dashboard: {
      title: "📊 Tableau de Bord - Accompagnement",
      refresh: "Actualiser",
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
      refresh: "Actualiser",
      filters: {
        priority: "Priorité:",
        status: "Statut:",
      },
    },
  },
  en: {
    chat: {
      welcome: {
        long: `Hello and welcome to Mobilier de France customer support. We are here to help you.\n\nTo assist quickly, please provide:\n• Your name\n• Your order number\n• A description of your issue\n\nYou can type or use the microphone 🎤`,
        short:
          "Hello and welcome to Mobilier de France customer support. Please provide your name, order number and issue description.",
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
    },
    dashboard: {
      title: "📊 Dashboard - Support",
      refresh: "Refresh",
      filters: {
        priority: "Priority:",
        status: "Status:",
      },
    },
  },
  ar: {
    chat: {
      welcome: {
        long: `مرحبًا بك في خدمة عملاء مجموعة Mobilier de France. نحن هنا لمساعدتك.\n\nللمساعدة السريعة، يرجى تقديم:\n• اسمك\n• رقم الطلب\n• وصف المشكلة\n\nيمكنك الكتابة أو استخدام الميكروفون 🎤`,
        short:
          "مرحبًا بك في خدمة عملاء Mobilier de France. الرجاء تقديم اسمك ورقم الطلب ووصف المشكلة.",
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
    },
    dashboard: {
      title: "📊 لوحة التحكم - الدعم",
      refresh: "تحديث",
      filters: {
        priority: "الأولوية:",
        status: "الحالة:",
      },
    },
  },
};

export { supportedLanguages };
export default translations;
