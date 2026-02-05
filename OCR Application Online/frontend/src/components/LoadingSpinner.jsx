import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ message = 'Processing...' }) => {
    return (
        <div className="flex flex-col items-center justify-center py-12 animate-fade-in">
            <div className="relative">
                {/* Outer ring */}
                <div className="absolute inset-0 rounded-full border-4 border-primary-100"></div>

                {/* Spinning ring */}
                <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
            </div>

            <p className="mt-6 text-neutral-600 font-medium">{message}</p>

            {/* Animated dots */}
            <div className="flex gap-1 mt-3">
                <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
        </div>
    );
};

export default LoadingSpinner;
