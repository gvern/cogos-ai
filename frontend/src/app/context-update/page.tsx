'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import RadarChart from '@/components/features/RadarChart';
import ContextEditor from '@/components/features/ContextEditor';
import DomainProgress from '@/components/features/DomainProgress';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, RefreshCw, Save } from 'lucide-react';

// Données initiales pour le contexte (en attendant l'intégration de l'API)
const sampleContext = {
    name: "Alice Johnson",
    role: "Product Manager",
    tone: "Professional and concise",
    goals: ["Increase team productivity", "Improve product quality", "Enhance user experience"],
    focusItems: ["Q2 Roadmap", "User feedback analysis", "Team collaboration"],
    domains: {
        technology: 8,
        business: 7,
        communication: 6,
        leadership: 9,
        creativity: 5,
        analytics: 8
    }
};

export default function ContextUpdatePage() {
    const router = useRouter();
    const [context, setContext] = useState(sampleContext);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState("edit");

    // Simuler le chargement des données depuis une API
    const loadContextData = async () => {
        setLoading(true);
        try {
            // Ici, nous simulons une requête API
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Dans une implémentation réelle, les données viendraient de l'API
            // setContext(await fetchContextFromAPI());

            toast.success("Context data loaded successfully");
        } catch (error) {
            toast.error("Failed to load context data");
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    // Simuler la sauvegarde du contexte vers une API
    const saveContext = async (updatedContext: any) => {
        setLoading(true);
        try {
            // Ici, nous simulons une requête API
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Dans une implémentation réelle, nous enverrions les données à l'API
            // await saveContextToAPI(updatedContext);

            setContext(updatedContext);
            toast.success("Context updated successfully");
        } catch (error) {
            toast.error("Failed to update context");
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    // Charger les données au chargement de la page
    useEffect(() => {
        loadContextData();
    }, []);

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <h1 className="text-2xl font-bold">Context Update</h1>
                </div>
                <Button
                    variant="default"
                    disabled={loading}
                    onClick={() => loadContextData()}
                >
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                </Button>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-8">
                    <TabsTrigger value="edit">Edit Context</TabsTrigger>
                    <TabsTrigger value="visualize">Visualize</TabsTrigger>
                </TabsList>

                <TabsContent value="edit" className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <ContextEditor
                            initialContext={context}
                            onSave={saveContext}
                            isLoading={loading}
                            onRefresh={loadContextData}
                        />
                        <DomainProgress
                            domains={context.domains || {}}
                            title="Your Domain Scores"
                            description="Current scores across key knowledge domains"
                        />
                    </div>
                </TabsContent>

                <TabsContent value="visualize">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <RadarChart
                            domains={context.domains || {}}
                            title="Domain Knowledge Radar"
                            colorScheme="rainbow"
                        />
                        <div className="space-y-6">
                            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
                                <h2 className="text-xl font-semibold mb-4">Context Summary</h2>
                                <div className="space-y-4">
                                    <div>
                                        <span className="font-medium text-gray-700 dark:text-gray-300">Name:</span>
                                        <span className="ml-2 text-gray-600 dark:text-gray-400">{context.name}</span>
                                    </div>
                                    <div>
                                        <span className="font-medium text-gray-700 dark:text-gray-300">Role:</span>
                                        <span className="ml-2 text-gray-600 dark:text-gray-400">{context.role}</span>
                                    </div>
                                    <div>
                                        <span className="font-medium text-gray-700 dark:text-gray-300">Tone:</span>
                                        <span className="ml-2 text-gray-600 dark:text-gray-400">{context.tone}</span>
                                    </div>
                                    <div>
                                        <span className="font-medium text-gray-700 dark:text-gray-300">Goals:</span>
                                        <ul className="ml-6 list-disc mt-2 text-gray-600 dark:text-gray-400">
                                            {context.goals.map((goal, index) => (
                                                <li key={index}>{goal}</li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div>
                                        <span className="font-medium text-gray-700 dark:text-gray-300">Focus Items:</span>
                                        <ul className="ml-6 list-disc mt-2 text-gray-600 dark:text-gray-400">
                                            {context.focusItems.map((item, index) => (
                                                <li key={index}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <Button className="w-full" onClick={() => setActiveTab("edit")}>
                                <Save className="mr-2 h-4 w-4" />
                                Edit Context
                            </Button>
                        </div>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
