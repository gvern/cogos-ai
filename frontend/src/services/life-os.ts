import { LifeOSData, Goal, LifeOSStats } from '@/types/life-os';

const API_URL = 'http://localhost:8000/api/v1/life-os';

export const LifeOSService = {
    async getData(): Promise<LifeOSData> {
        const response = await fetch(`${API_URL}/goals`);
        if (!response.ok) throw new Error('Failed to fetch LifeOS data');
        return response.json();
    },

    async updateGoal(goal: Goal): Promise<Goal> {
        const response = await fetch(`${API_URL}/goals/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(goal),
        });
        if (!response.ok) throw new Error('Failed to update goal');
        return response.json();
    },

    async deleteGoal(goalId: string): Promise<void> {
        const response = await fetch(`${API_URL}/goals/delete/${goalId}`, {
            method: 'POST',
        });
        if (!response.ok) throw new Error('Failed to delete goal');
    },

    async getStats(): Promise<LifeOSStats> {
        const response = await fetch(`${API_URL}/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        return response.json();
    }
};
