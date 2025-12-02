'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Home,
  MessageSquare,
  Calendar,
  RefreshCw,
  Folder,
  Brain,
  Edit,
  Compass,
  Cpu,
  Menu,
  X,
  MoonStar,
  Sun,
  Network
} from 'lucide-react';
import { useCogosStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { useTheme } from 'next-themes';

interface NavItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: <Home size={20} /> },
  { name: 'Conversation', href: '/conversation', icon: <MessageSquare size={20} /> },
  { name: 'Constellation', href: '/constellation', icon: <Network size={20} /> },
  { name: 'Timeline', href: '/timeline', icon: <Calendar size={20} /> },
  { name: 'Contexte', href: '/context', icon: <RefreshCw size={20} /> },
  { name: 'Mémoire', href: '/memory', icon: <Folder size={20} /> },
  { name: 'Réflexion', href: '/reflection', icon: <Brain size={20} /> },
  { name: 'Édition', href: '/edit-memory', icon: <Edit size={20} /> },
  { name: 'Second Brain', href: '/second-brain', icon: <Brain size={20} /> },
  { name: 'Skills', href: '/skills', icon: <Compass size={20} /> },
  { name: 'Agent', href: '/agent', icon: <Cpu size={20} /> },
];

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();

  const jarvisMode = useCogosStore(state => state.isJarvisMode);
  const setJarvisMode = useCogosStore(state => state.setJarvisMode);

  // Fermer le menu sur petit écran lors de la navigation
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  return (
    <>
      {/* Bouton menu mobile */}
      <div className="block md:hidden fixed top-4 left-4 z-50">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setIsOpen(!isOpen)}
          className="bg-white dark:bg-gray-800 shadow-md"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </Button>
      </div>

      {/* Overlay pour fermer le menu sur mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-64 bg-white dark:bg-gray-900 shadow-lg z-40
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 md:relative md:z-0 md:shadow-none
          border-r border-gray-200 dark:border-gray-800
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo et titre */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-800">
            <div className="flex items-center space-x-2">
              <Brain className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">CogOS</h1>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Votre système cognitif personnel
            </p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 overflow-y-auto">
            <ul className="space-y-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link href={item.href}>
                      <span
                        className={`
                          flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium
                          ${isActive
                            ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                            : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}
                          transition-colors
                          relative
                        `}
                      >
                        {item.icon}
                        <span>{item.name}</span>
                        {isActive && (
                          <div
                            className="absolute left-0 w-1 h-8 bg-blue-600 dark:bg-blue-400 rounded-r-full"
                          />
                        )}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-800 space-y-3">
            {/* Mode JARVIS */}
            <Button
              variant={jarvisMode ? "jarvis" : "outline"}
              className="w-full justify-start"
              onClick={() => setJarvisMode(!jarvisMode)}
            >
              <Cpu className="mr-2 h-4 w-4" />
              <span>{jarvisMode ? "JARVIS activé" : "Mode JARVIS"}</span>
            </Button>

            {/* Switch thème */}
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              <div className="relative w-4 h-4 mr-2">
                <Sun className="absolute inset-0 h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <MoonStar className="absolute inset-0 h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              </div>
              <span>{theme === 'dark' ? 'Mode sombre' : 'Mode clair'}</span>
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;