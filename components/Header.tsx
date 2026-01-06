
import React from 'react';
import { DuplicateIcon } from './icons';

export const Header: React.FC = () => (
  <header className="bg-gray-800 shadow-lg">
    <div className="container mx-auto px-4 md:px-8 py-4 flex items-center gap-4">
      <DuplicateIcon className="w-8 h-8 text-cyan-400" />
      <h1 className="text-2xl font-bold tracking-tight text-white">
        Duplicate Image Finder
      </h1>
    </div>
  </header>
);
