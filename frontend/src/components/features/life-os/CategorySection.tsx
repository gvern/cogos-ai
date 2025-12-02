import React from 'react';
import { Category, Goal } from '@/types/life-os';
import { GoalCard } from './GoalCard';
import * as Icons from 'lucide-react';

interface CategorySectionProps {
    category: Category;
    goals: Goal[];
    onUpdateGoal: (goal: Goal) => void;
}

export const CategorySection: React.FC<CategorySectionProps> = ({ category, goals, onUpdateGoal }) => {
    // Dynamic Icon
    const IconComponent = (Icons as any)[category.icon] || Icons.Circle;

    const completedCount = goals.filter(g => g.status === 'completed').length;
    const progress = goals.length > 0 ? Math.round((completedCount / goals.length) * 100) : 0;

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-${category.color}-100 text-${category.color}-600`}>
                        <IconComponent className="w-5 h-5" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-slate-800">{category.name}</h3>
                        <p className="text-xs text-slate-500">{completedCount}/{goals.length} completed</p>
                    </div>
                </div>
                <div className="w-12 h-12 relative flex items-center justify-center">
                    {/* Circular Progress (Simplified) */}
                    <span className="text-xs font-bold text-slate-700">{progress}%</span>
                </div>
            </div>

            <div className="p-4 space-y-3">
                {goals.map(goal => (
                    <GoalCard
                        key={goal.id}
                        goal={goal}
                        onToggle={(g) => {
                            const newStatus = g.status === 'completed' ? 'todo' : 'completed';
                            const newProgress = newStatus === 'completed' ? 100 : 0;
                            onUpdateGoal({ ...g, status: newStatus, progress: newProgress });
                        }}
                    />
                ))}
                {goals.length === 0 && (
                    <p className="text-sm text-slate-400 text-center py-4">No goals yet</p>
                )}
            </div>
        </div>
    );
};
