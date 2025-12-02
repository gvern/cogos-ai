'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error(error);
    }, [error]);

    return (
        <div className="flex flex-col items-center justify-center h-screen space-y-4 bg-white dark:bg-slate-900">
            <div className="p-4 bg-red-50 text-red-600 rounded-full">
                <AlertTriangle className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Something went wrong!</h2>
            <p className="text-slate-500 dark:text-slate-400 max-w-md text-center">
                {error.message || "An unexpected error occurred."}
            </p>
            <Button onClick={() => reset()}>
                Try again
            </Button>
        </div>
    );
}
