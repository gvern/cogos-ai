import { RefreshCw } from 'lucide-react';

export default function Loading() {
    return (
        <div className="flex flex-col items-center justify-center h-[50vh] text-slate-400">
            <RefreshCw className="w-8 h-8 animate-spin mb-4 text-indigo-500" />
            <p>Loading Second Brain...</p>
        </div>
    );
}
