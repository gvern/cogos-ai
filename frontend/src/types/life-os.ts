export type GoalStatus = 'todo' | 'in_progress' | 'completed';

export interface Category {
    id: string;
    name: string;
    icon: string;
    color: string;
}

export interface Goal {
    id: string;
    categoryId: string;
    title: string;
    status: GoalStatus;
    progress: number;
    notes?: string;
    deadline?: string;
}

export interface LifeOSData {
    categories: Category[];
    goals: Goal[];
}

export interface LifeOSStats {
    total: number;
    completed: number;
    in_progress: number;
    todo: number;
    completion_rate: number;
}
