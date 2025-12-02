import React from 'react';
import { Goal } from '@/types/life-os';
import { CheckCircle2, Circle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GoalCardProps {
    goal: Goal;
    onToggle: (goal: Goal) => void;
}

export const GoalCard: React.FC<GoalCardProps> = ({ goal, onToggle }) => {
    const isCompleted = goal.status === 'completed';
    const isInProgress = goal.status === 'in_progress';

    return (
        <div
            className={cn(
                "group flex items-start gap-3 p-3 rounded-lg border transition-all hover:shadow-sm",
                isCompleted ? "bg-green-50/50 border-green-100" : "bg-white border-slate-100 hover:border-slate-200"
            )}
        >
            <button
                onClick={() => onToggle(goal)}
                className={cn(
                    "mt-0.5 flex-shrink-0 transition-colors",
                    isCompleted ? "text-green-500" : "text-slate-300 hover:text-slate-400"
                )}
            >
                {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5" />
                ) : (
                    <Circle className="w-5 h-5" />
                )}
            </button>

            <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                    <h4 className={cn(
                        "text-sm font-medium truncate",
                        isCompleted ? "text-slate-500 line-through" : "text-slate-700"
                    )}>
                        {goal.title}
                    </h4>
                    {isInProgress && (
                        <span className="flex items-center gap-1 text-xs font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                            <Clock className="w-3 h-3" />
                            {goal.progress}%
                        </span>
                    )}
                </div>

                {goal.notes && (
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                        {goal.notes}
                    </p>
                )}

                {/* Progress Bar for in-progress items */}
                {isInProgress && (
                    <div className="mt-2 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-amber-500 rounded-full transition-all duration-500"
                            style={{ width: `${goal.progress}%` }}
                        />
                    </div>
                )}
            </div>
        </div>
    );
};
