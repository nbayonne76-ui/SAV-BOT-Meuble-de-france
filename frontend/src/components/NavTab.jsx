import { memo } from "react";

const NavTab = memo(({ icon: Icon, label, isActive, onClick, colors }) => {
  return (
    <button
      onClick={onClick}
      className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
      style={{
        backgroundColor: isActive
          ? colors.background.light
          : colors.accent.primary,
        color: isActive ? colors.text.primary : colors.text.secondary,
      }}
    >
      <Icon className="w-5 h-5" />
      <span>{label}</span>
    </button>
  );
});

NavTab.displayName = "NavTab";

export default NavTab;
