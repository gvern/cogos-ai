import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UserSettings {
    theme: 'light' | 'dark' | 'system';
    notifications: boolean;
    sound: boolean;
}

interface CogosState {
    isJarvisMode: boolean;
    setJarvisMode: (isJarvisMode: boolean) => void;
    userSettings: UserSettings;
    updateUserSettings: (settings: Partial<UserSettings>) => void;
}

export const useCogosStore = create<CogosState>()(
    persist(
        (set) => ({
            isJarvisMode: false,
            setJarvisMode: (isJarvisMode) => set({ isJarvisMode }),
            userSettings: {
                theme: 'system',
                notifications: true,
                sound: true,
            },
            updateUserSettings: (settings) =>
                set((state) => ({
                    userSettings: { ...state.userSettings, ...settings },
                })),
        }),
        {
            name: 'cogos-storage',
        }
    )
);
