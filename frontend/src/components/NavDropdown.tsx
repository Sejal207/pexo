import React, { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronDown, LucideIcon } from 'lucide-react';

interface NavDropdownItem {
  label: string;
  to: string;
}

interface NavDropdownProps {
  label: string;
  icon: LucideIcon;
  items: NavDropdownItem[];
}

export const NavDropdown: React.FC<NavDropdownProps> = ({ label, icon: Icon, items }) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  const isActive = items.some((item) => location.pathname.startsWith(item.to));

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition ${
          isActive
            ? 'bg-slate-700/50 text-white'
            : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
        }`}
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <Icon className="w-4 h-4" />
        <span>{label}</span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div
          className="absolute left-0 mt-2 w-48 rounded-lg border border-slate-700/60 bg-slate-800 shadow-lg py-1 z-50"
          role="menu"
        >
          {items.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="block px-4 py-2 text-sm text-slate-300 hover:bg-slate-700/40 hover:text-white transition"
              role="menuitem"
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};