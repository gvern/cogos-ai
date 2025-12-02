'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings } from 'lucide-react';

export default function SettingsPage() {
    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex flex-col gap-6">
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold">Paramètres</h1>
                    <p className="text-gray-500 dark:text-gray-400">
                        Configuration et préférences du système
                    </p>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Settings className="h-5 w-5" />
                            Configuration
                        </CardTitle>
                        <CardDescription>
                            Cette page est en cours de développement
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-gray-600 dark:text-gray-300">
                            L'interface de configuration sera bientôt disponible.
                            Elle permettra de personnaliser les paramètres de l'agent et de l'interface.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
