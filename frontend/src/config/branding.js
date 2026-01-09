// // frontend/src/config/branding.js
// /**
//  * Configuration du branding et des couleurs de l'interface
//  * Modifiez ces valeurs pour personnaliser l'apparence de l'application
//  */

// export const branding = {
//   // COULEURS PRINCIPALES - MOBILIER DE FRANCE
//   colors: {
//     // Fond d'écran principal (inspiré du site Mobilier de France)
//     background: {
//       primary: '#20253F',    // Bleu foncé - RVB(32, 37, 63)
//       secondary: '#2C3650',  // Bleu Mobilier de France (footer)
//       light: '#3A3F5A',      // Variante encore plus claire pour les hover
//     },

//     // Texte
//     text: {
//       primary: '#FFFFFF',    // Blanc - RVB(255, 255, 255)
//       secondary: '#E0E0E0',  // Gris clair pour texte secondaire
//       muted: '#A0A0A0',      // Gris pour texte atténué
//     },

//     // Accents Mobilier de France (bleu professionnel)
//     accent: {
//       primary: '#2C3650',    // Bleu Mobilier de France pour boutons principaux
//       secondary: '#3A4560',  // Bleu plus clair pour accents
//       success: '#10B981',    // Vert pour succès
//       warning: '#F59E0B',    // Orange pour avertissements
//       error: '#EF4444',      // Rouge pour erreurs
//       info: '#2C3650',       // Bleu Mobilier de France pour informations
//     },

//     // Priorités d'accompagnement
//     priority: {
//       P0: '#DC2626',         // Rouge critique
//       P1: '#EA580C',         // Orange urgent
//       P2: '#F59E0B',         // Jaune modéré
//       P3: '#10B981',         // Vert faible
//     },
//   },

//   // TYPOGRAPHIE
//   fonts: {
//     primary: '"Segoe UI Variable Display Semib", "Segoe UI", system-ui, -apple-system, sans-serif',
//     fallback: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
//   },

//   // ESPACEMENT
//   spacing: {
//     xs: '0.25rem',
//     sm: '0.5rem',
//     md: '1rem',
//     lg: '1.5rem',
//     xl: '2rem',
//     xxl: '3rem',
//   },

//   // BORDURES
//   borderRadius: {
//     sm: '0.25rem',
//     md: '0.5rem',
//     lg: '0.75rem',
//     xl: '1rem',
//     full: '9999px',
//   },
// };

// // Fonction helper pour générer les classes Tailwind personnalisées
// export const getBrandingClasses = () => {
//   return {
//     background: `bg-[${branding.colors.background.primary}]`,
//     text: `text-[${branding.colors.text.primary}]`,
//     font: `font-['Segoe_UI_Variable_Display_Semib']`,
//   };
// };

// export default branding;

export default {
  colors: {
    background: {
      // primary: "#F9FAFB",
      // secondary: "#FFFFFF",
      // light: "#F3F4F6",
      primary: "#20253F", // Bleu foncé - RVB(32, 37, 63)
      secondary: "#2C3650", // Bleu Mobilier de France (footer)
      light: "#3A3F5A", // Variante encore plus claire pour les hover
    },
    accent: {
      // primary: "#DC2626",
      // secondary: "#EA580C",
      primary: "#2C3650", // Bleu Mobilier de France pour boutons principaux
      secondary: "#3A4560", // Bleu plus clair pour accents
      success: "#10B981", // Vert pour succès
      warning: "#F59E0B", // Orange pour avertissements
      error: "#EF4444", // Rouge pour erreurs
      info: "#2C3650", // Bleu Mobilier de France pour informations
    },
    text: {
      // primary: "#111827",
      // secondary: "#6B7280",
      primary: "#FFFFFF", // Blanc - RVB(255, 255, 255)
      secondary: "#E0E0E0", // Gris clair pour texte secondaire
      muted: "#A0A0A0", // Gris pour texte atténué
    },
  },
  priority: {
    P0: "#DC2626", // Rouge critique
    P1: "#EA580C", // Orange urgent
    P2: "#F59E0B", // Jaune modéré
    P3: "#10B981", // Vert faible
  },
  fonts: {
    // primary: "'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif",
    primary:
      '"Segoe UI Variable Display Semib", "Segoe UI", system-ui, -apple-system, sans-serif',
    fallback: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
  },
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
    xxl: "3rem",
  },

  // BORDURES
  borderRadius: {
    sm: "0.25rem",
    md: "0.5rem",
    lg: "0.75rem",
    xl: "1rem",
    full: "9999px",
  },
};
export const getBrandingClasses = () => {
  return {
    background: `bg-[${branding.colors.background.primary}]`,
    text: `text-[${branding.colors.text.primary}]`,
    font: `font-['Segoe_UI_Variable_Display_Semib']`,
  };
};
