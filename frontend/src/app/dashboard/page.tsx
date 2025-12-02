'use client';

import React from 'react';
import RadarChart from '@/components/features/RadarChart';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageSquare, Calendar, Brain, Folder, Zap, User, Settings, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';

// Données de démonstration
const mockDomainData = {
    technology: 8,
    business: 7,
    communication: 6,
    leadership: 9,
    creativity: 5,
    analytics: 8
};

const quickActions = [
    { name: 'Nouvelle conversation', href: '/conversation', icon: <MessageSquare className="h-4 w-4" /> },
    { name: 'Mise à jour contexte', href: '/context-update', icon: <RefreshCw className="h-4 w-4" /> },
    { name: 'Mémoire', href: '/memory', icon: <Folder className="h-4 w-4" /> },
    { name: 'Paramètres', href: '/settings', icon: <Settings className="h-4 w-4" /> },
];

const insightsData = [
    { title: 'Mémoires récentes', value: '12', change: '+3', description: 'Nouveaux éléments cette semaine' },
    { title: 'Réflexions', value: '4', change: '+1', description: 'Nouvelles réflexions générées' },
    { title: 'Conversations', value: '28', change: '+5', description: 'Interactions récentes' },
];

export default function Dashboard() {
    return (
        <div className="mx-auto max-w-7xl p-6">
            <div className="flex flex-col gap-6">
                {/* En-tête */}
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold">Tableau de bord</h1>
                    <p className="text-gray-500 dark:text-gray-400">
                        Bienvenue dans votre espace cognitif personnel
                    </p>
                </div>

                {/* Statistiques rapides */}
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {insightsData.map((item, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, delay: i * 0.1 }}
                        >
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between pb-2">
                                    <CardTitle className="text-sm font-medium">
                                        {item.title}
                                    </CardTitle>
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth="2"
                                        className="h-4 w-4 text-gray-500 dark:text-gray-400"
                                    >
                                        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                                    </svg>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold">{item.value}</div>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        {item.change && (
                                            <span className={item.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}>
                                                {item.change}
                                            </span>
                                        )}{' '}
                                        {item.description}
                                    </p>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </div>

                {/* Graphique et Actions */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4 }}
                    >
                        <RadarChart
                            domains={mockDomainData}
                            title="Profil de Connaissances"
                            colorScheme="blue"
                        />
                    </motion.div>

                    <div className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Actions rapides</CardTitle>
                                <CardDescription>
                                    Accédez rapidement aux fonctionnalités principales
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="grid grid-cols-2 gap-4">
                                {quickActions.map((action, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        transition={{ duration: 0.3, delay: i * 0.1 }}
                                    >
                                        <Link href={action.href}>
                                            <Button
                                                variant="outline"
                                                className="w-full justify-start"
                                            >
                                                <span className="mr-2">{action.icon}</span>
                                                {action.name}
                                            </Button>
                                        </Link>
                                    </motion.div>
                                ))}
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Mode JARVIS</CardTitle>
                                <CardDescription>
                                    Activez l'interface de conversation avancée
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Le mode JARVIS vous offre une expérience plus immersive avec votre système cognitif personnel.
                                </p>
                            </CardContent>
                            <CardFooter>
                                <Button variant="jarvis" className="w-full">
                                    <Brain className="mr-2 h-4 w-4" />
                                    Activer JARVIS
                                </Button>
                            </CardFooter>
                        </Card>
                    </div>
                </div>

                {/* Suggestions et Insights */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                    <Card className="md:col-span-2">
                        <CardHeader>
                            <CardTitle>Suggestions de réflexion</CardTitle>
                            <CardDescription>
                                Basées sur vos activités récentes
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ul className="space-y-4">
                                <li className="flex items-start space-x-3">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
                                        <Zap className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                                    </div>
                                    <div>
                                        <p className="font-medium">Analyser vos habitudes de travail</p>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">
                                            Nous avons détecté des patterns dans votre utilisation quotidienne
                                        </p>
                                    </div>
                                </li>
                                <li className="flex items-start space-x-3">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                                        <Brain className="h-4 w-4 text-green-600 dark:text-green-400" />
                                    </div>
                                    <div>
                                        <p className="font-medium">Améliorer votre prise de décision</p>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">
                                            Explorez des méthodes de raisonnement systématique
                                        </p>
                                    </div>
                                </li>
                                <li className="flex items-start space-x-3">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900">
                                        <Calendar className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                                    </div>
                                    <div>
                                        <p className="font-medium">Planifier votre semaine</p>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">
                                            Utilisez l'assistant pour générer un plan de la semaine
                                        </p>
                                    </div>
                                </li>
                            </ul>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Votre contexte</CardTitle>
                            <CardDescription>
                                Profil actuel
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center space-x-4">
                                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
                                    <User className="h-6 w-6 text-gray-600 dark:text-gray-400" />
                                </div>
                                <div>
                                    <p className="font-medium">Alice Johnson</p>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                        Product Manager
                                    </p>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <p className="text-sm font-medium">Objectifs principaux:</p>
                                <ul className="text-sm text-gray-500 dark:text-gray-400 space-y-1 list-disc list-inside">
                                    <li>Améliorer la productivité</li>
                                    <li>Développer de nouvelles compétences</li>
                                    <li>Organiser les connaissances</li>
                                </ul>
                            </div>
                            <div className="pt-2">
                                <Link href="/context-update">
                                    <Button variant="outline" size="sm" className="w-full">
                                        <RefreshCw className="mr-2 h-3 w-3" />
                                        Mettre à jour
                                    </Button>
                                </Link>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
