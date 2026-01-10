import { memo } from "react";
import { Link } from "react-router-dom";

const NavTab = memo(({ icon: Icon, label, isActive, onClick, colors, to }) => {
  const commonClass =
    "flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 font-medium text-sm hover:opacity-80 relative pb-3";
  const style = {
    backgroundColor: isActive ? colors.background.light : colors.accent.primary,
    color: isActive ? colors.text.primary : colors.text.secondary,
  };

  if (to) {
    return (
      <Link
        to={to}
        className={commonClass}
        style={style}
        aria-current={isActive ? "page" : undefined}
      >
        <Icon className="w-5 h-5" />
        <span>{label}</span>
        {isActive && (
          <div
            className="absolute bottom-0 left-0 right-0 h-1 rounded-t-full"
            style={{ backgroundColor: colors.accent.primary }}
          />
        )}
      </Link>
    );
  }

  return (
    <button onClick={onClick} className={commonClass} style={style}>
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
