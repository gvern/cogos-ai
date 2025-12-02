import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface DomainProgressProps {
  domains: Record<string, number>;
  maxValue?: number;
  title?: string;
  description?: string;
}

// Fonction pour déterminer la couleur de la barre de progression en fonction du score
const getProgressColor = (score: number, maxValue: number): string => {
  const percentage = (score / maxValue) * 100;
  
  if (percentage < 30) return 'bg-red-500';
  if (percentage < 60) return 'bg-amber-500';
  if (percentage < 80) return 'bg-blue-500';
  return 'bg-green-500';
};

export const DomainProgress = ({
  domains,
  maxValue = 10,
  title = 'Domain Analysis',
  description = 'Current scores across key domains'
}: DomainProgressProps) => {
  // Trier les domaines par score (du plus élevé au plus bas)
  const sortedDomains = Object.entries(domains)
    .sort(([, scoreA], [, scoreB]) => scoreB - scoreA);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="w-full shadow-md">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {sortedDomains.map(([domain, score], index) => {
            const formattedDomain = domain.charAt(0).toUpperCase() + domain.slice(1);
            const progressColor = getProgressColor(score, maxValue);
            const percentage = (score / maxValue) * 100;
            
            return (
              <motion.div 
                key={domain}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="space-y-1"
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {formattedDomain}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {score}/{maxValue}
                  </span>
                </div>
                <Progress 
                  value={percentage} 
                  className="h-2"
                  indicatorClassName={cn(progressColor, "transition-all duration-500")}
                />
              </motion.div>
            );
          })}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default DomainProgress; 