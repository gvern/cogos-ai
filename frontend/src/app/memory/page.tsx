'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Folder } from 'lucide-react';

export default function MemoryPage() {
    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex flex-col gap-6">
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold">Mémoire</h1>
                    <p className="text-gray-500 dark:text-gray-400">
                        Gestion et visualisation de la mémoire de l'agent
                    </p>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Folder className="h-5 w-5" />
                            Système de mémoire
                        </CardTitle>
                        <CardDescription>
                            Cette page est en cours de développement
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-gray-600 dark:text-gray-300">
                            L'interface de gestion de la mémoire sera bientôt disponible.
                            Elle permettra de visualiser et organiser les connaissances de l'agent.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
