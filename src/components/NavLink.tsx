import { NavLink as RouterNavLink, NavLinkProps } from "react-router-dom";
import { forwardRef } from "react";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  TrendingUp,
  MessageSquare,
  Calendar,
  User,
  LucideIcon,
} from "lucide-react";

interface NavLinkCompatProps extends Omit<NavLinkProps, "className"> {
  className?: string;
  activeClassName?: string;
  pendingClassName?: string;
  icon?: string;
  label?: string;
  collapsed?: boolean;
}

const iconMap: Record<string, LucideIcon> = {
  LayoutDashboard,
  TrendingUp,
  MessageSquare,
  Calendar,
  User,
};

const NavLink = forwardRef<HTMLAnchorElement, NavLinkCompatProps>(
  ({ className, activeClassName, pendingClassName, to, icon, label, collapsed, ...props }, ref) => {
    const IconComponent = icon ? iconMap[icon] : null;

    return (
      <RouterNavLink
        ref={ref}
        to={to}
        className={({ isActive, isPending }) =>
          cn(
            "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
            isActive && "bg-accent text-accent-foreground",
            isPending && "text-muted-foreground",
            className,
            isActive && activeClassName,
            isPending && pendingClassName
          )
        }
        {...props}
      >
        {IconComponent && <IconComponent className="h-5 w-5 flex-shrink-0" />}
        {!collapsed && label && <span>{label}</span>}
      </RouterNavLink>
    );
  },
);

NavLink.displayName = "NavLink";

export { NavLink };
