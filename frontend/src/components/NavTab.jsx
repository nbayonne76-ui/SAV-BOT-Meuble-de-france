import { memo } from "react";

const NavTab = memo(({ icon: Icon, label, isActive, onClick, colors }) => {
  return (
    <button
      onClick={onClick}
      className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 font-medium text-sm hover:opacity-80 relative pb-3"
      style={{
        backgroundColor: isActive
          ? colors.background.light
          : colors.accent.primary,
        color: isActive ? colors.text.primary : colors.text.secondary,
      }}
    >
      <Icon className="w-5 h-5" />
      <span>{label}</span>
      {isActive && (
        <div
          className="absolute bottom-0 left-0 right-0 h-1 rounded-t-full"
          style={{ backgroundColor: colors.accent.primary }}
        />
      )}
    </button>
  );
});

NavTab.displayName = "NavTab";

export default NavTab;
