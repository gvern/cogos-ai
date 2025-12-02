import React, { useEffect } from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import { motion } from 'framer-motion';

// Enregistrer les composants Chart.js nécessaires
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface RadarChartProps {
  domains: Record<string, number>;
  title?: string;
  maxValue?: number;
  colorScheme?: 'blue' | 'purple' | 'green' | 'rainbow';
}

const getColorScheme = (scheme: string) => {
  switch (scheme) {
    case 'purple':
      return {
        bgColor: 'rgba(124, 58, 237, 0.2)',
        borderColor: 'rgba(124, 58, 237, 1)',
        pointBgColor: 'rgba(124, 58, 237, 1)',
      };
    case 'green':
      return {
        bgColor: 'rgba(16, 185, 129, 0.2)',
        borderColor: 'rgba(16, 185, 129, 1)',
        pointBgColor: 'rgba(16, 185, 129, 1)',
      };
    case 'rainbow':
      return {
        bgColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
        ],
        pointBgColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
        ],
      };
    case 'blue':
    default:
      return {
        bgColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        pointBgColor: 'rgba(59, 130, 246, 1)',
      };
  }
};

export const RadarChart = ({
  domains,
  title = 'Scores par domaine',
  maxValue = 10,
  colorScheme = 'blue',
}: RadarChartProps) => {
  // Obtenir les noms des domaines et les scores
  const labels = Object.keys(domains).map(key => key.charAt(0).toUpperCase() + key.slice(1));
  const scores = Object.values(domains);
  
  // Obtenir les couleurs selon le schéma choisi
  const colors = getColorScheme(colorScheme);
  
  // Configurer les données pour le graphique
  const data = {
    labels,
    datasets: [
      {
        label: title,
        data: scores,
        backgroundColor: colors.bgColor,
        borderColor: colors.borderColor,
        borderWidth: 2,
        pointBackgroundColor: colors.pointBgColor,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(59, 130, 246, 1)',
        pointLabelFontSize: 14,
      },
    ],
  };
  
  // Options du graphique
  const options = {
    scales: {
      r: {
        angleLines: {
          display: true,
        },
        suggestedMin: 0,
        suggestedMax: maxValue,
        ticks: {
          stepSize: 2,
          font: {
            size: 10,
          },
          backdropColor: 'transparent',
        },
        pointLabels: {
          font: {
            size: 12,
            weight: 'bold',
          },
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        titleFont: {
          size: 14,
        },
        bodyFont: {
          size: 13,
        },
        padding: 10,
        displayColors: false,
      },
    },
    elements: {
      line: {
        tension: 0.2,
      },
    },
    maintainAspectRatio: false,
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md"
    >
      <h3 className="text-lg font-medium mb-4 text-gray-800 dark:text-gray-200 text-center">
        {title}
      </h3>
      <div className="h-72 w-full">
        <Radar data={data} options={options as any} />
      </div>
    </motion.div>
  );
};

export default RadarChart; 