"use client";

import React, { useEffect, useState } from 'react';
import { LifeOSData, Goal } from '@/types/life-os';
import { LifeOSService } from '@/services/life-os';
import { CategorySection } from '@/components/features/life-os/CategorySection';
import { Brain, RefreshCw } from 'lucide-react';

export default function SecondBrainPage() {
    const [data, setData] = useState<LifeOSData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            const result = await LifeOSService.getData();
            setData(result);
            setError(null);
        } catch (err) {
            console.error(err);
            setError('Failed to load Second Brain data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleUpdateGoal = async (goal: Goal) => {
        try {
            // Optimistic update
            if (data) {
                const updatedGoals = data.goals.map(g => g.id === goal.id ? goal : g);
                setData({ ...data, goals: updatedGoals });
            }

            await LifeOSService.updateGoal(goal);
        } catch (err) {
            console.error(err);
            // Revert on error (could be improved)
            fetchData();
        }
    };

    if (loading && !data) {
        return (
            <div className="flex items-center justify-center h-screen text-slate-400">
                <RefreshCw className="w-6 h-6 animate-spin mr-2" />
                Loading Second Brain...
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen text-red-500">
                {error}
            </div>
        );
    }

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <header className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-3 bg-indigo-100 text-indigo-600 rounded-xl">
                        <Brain className="w-8 h-8" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">Second Brain</h1>
                        <p className="text-slate-500">Track your life goals, habits, and skills.</p>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 masonry-grid">
                {data?.categories.map(category => {
                    const categoryGoals = data.goals.filter(g => g.categoryId === category.id);
                    return (
                        <CategorySection
                            key={category.id}
                            category={category}
                            goals={categoryGoals}
                            onUpdateGoal={handleUpdateGoal}
                        />
                    );
                })}
            </div>
        </div>
    );
}
