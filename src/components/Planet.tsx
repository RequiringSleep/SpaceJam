// src/components/ui/Planet.tsx
"use client";

import React from 'react';

interface PlanetProps {
    name: string;
    onClick: () => void;
}

const Planet: React.FC<PlanetProps> = ({ name, onClick }) => {
    const getPlanetStyle = () => {
        switch (name.toLowerCase()) {
            case 'earth':
                return `bg-gradient-to-r from-blue-400 via-green-400 to-blue-500 after:absolute after:inset-2 after:rounded-full after:border-2 after:border-blue-200/30`;
            case 'mars':
                return `bg-gradient-to-r from-red-500 via-red-400 to-red-500 after:absolute after:inset-2 after:rounded-full after:border-2 after:border-red-300/30`;
            default:
                return 'bg-gray-400';
        }
    };

    return (
        <button
            onClick={onClick}
            className={`w-16 h-16 rounded-full cursor-pointer relative ${getPlanetStyle()} 
                        hover:scale-105 transition-transform duration-300`}
            title={name}
        />
    );
};

export default Planet;
