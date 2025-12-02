import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout = ({ children }: MainLayoutProps) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex min-h-screen flex-col">
        <header className="sticky top-0 z-40 border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
          <div className="container flex h-16 items-center px-4 sm:px-6 lg:px-8">
            <div className="mr-4 flex">
              <a className="flex items-center" href="/">
                <span className="hidden text-xl font-bold sm:inline-block">
                  CogOS AI
                </span>
              </a>
            </div>
          </div>
        </header>
        <main className="flex-1">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {children}
          </motion.div>
        </main>
        <footer className="border-t border-gray-200 bg-white py-4 dark:border-gray-800 dark:bg-gray-950">
          <div className="container flex flex-col items-center justify-between gap-4 px-4 md:flex-row">
            <p className="text-center text-sm leading-loose text-gray-500 dark:text-gray-400 md:text-left">
              © {new Date().getFullYear()} CogOS AI. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default MainLayout; 