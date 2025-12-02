import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { PlusCircle, X, Save, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

export interface ContextData {
  name: string;
  role: string;
  tone: string;
  goals: string[];
  focusItems: string[];
  domains?: Record<string, number>;
}

interface ContextEditorProps {
  initialContext: ContextData;
  onSave: (context: ContextData) => void;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export const ContextEditor = ({
  initialContext,
  onSave,
  isLoading = false,
  onRefresh
}: ContextEditorProps) => {
  const [context, setContext] = useState<ContextData>(initialContext);
  const [newGoal, setNewGoal] = useState('');
  const [newFocusItem, setNewFocusItem] = useState('');

  useEffect(() => {
    setContext(initialContext);
  }, [initialContext]);

  const handleSave = () => {
    onSave(context);
    toast.success('Context updated successfully');
  };

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
      toast.info('Refreshing context data...');
    }
  };

  const addGoal = () => {
    if (newGoal.trim()) {
      setContext({
        ...context,
        goals: [...context.goals, newGoal.trim()]
      });
      setNewGoal('');
    }
  };

  const removeGoal = (index: number) => {
    setContext({
      ...context,
      goals: context.goals.filter((_, i) => i !== index)
    });
  };

  const addFocusItem = () => {
    if (newFocusItem.trim()) {
      setContext({
        ...context,
        focusItems: [...context.focusItems, newFocusItem.trim()]
      });
      setNewFocusItem('');
    }
  };

  const removeFocusItem = (index: number) => {
    setContext({
      ...context,
      focusItems: context.focusItems.filter((_, i) => i !== index)
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="w-full shadow-md">
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            <span>Context Editor</span>
            {onRefresh && (
              <Button
                variant="outline"
                size="icon"
                onClick={handleRefresh}
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            )}
          </CardTitle>
          <CardDescription>
            Modify your context to improve AI interactions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={context.name}
              onChange={(e) => setContext({ ...context, name: e.target.value })}
              placeholder="Your name"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Input
              id="role"
              value={context.role}
              onChange={(e) => setContext({ ...context, role: e.target.value })}
              placeholder="Your professional role"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="tone">Tone</Label>
            <Input
              id="tone"
              value={context.tone}
              onChange={(e) => setContext({ ...context, tone: e.target.value })}
              placeholder="Preferred communication tone"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="goals">Goals</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {context.goals.map((goal, index) => (
                <Badge key={index} variant="secondary" className="gap-1 px-2 py-1">
                  {goal}
                  <X
                    className="h-3 w-3 cursor-pointer text-gray-500 hover:text-red-500"
                    onClick={() => removeGoal(index)}
                  />
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                id="goals"
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                placeholder="Add a new goal"
                onKeyDown={(e) => e.key === 'Enter' && addGoal()}
              />
              <Button type="button" size="icon" onClick={addGoal}>
                <PlusCircle className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="focusItems">Focus Items</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {context.focusItems.map((item, index) => (
                <Badge key={index} variant="outline" className="gap-1 px-2 py-1">
                  {item}
                  <X
                    className="h-3 w-3 cursor-pointer text-gray-500 hover:text-red-500"
                    onClick={() => removeFocusItem(index)}
                  />
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                id="focusItems"
                value={newFocusItem}
                onChange={(e) => setNewFocusItem(e.target.value)}
                placeholder="Add a new focus item"
                onKeyDown={(e) => e.key === 'Enter' && addFocusItem()}
              />
              <Button type="button" size="icon" onClick={addFocusItem}>
                <PlusCircle className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button 
            type="submit" 
            className="w-full"
            onClick={handleSave}
            disabled={isLoading}
          >
            <Save className={`mr-2 h-4 w-4 ${isLoading ? 'animate-pulse' : ''}`} />
            Save Context
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
};

export default ContextEditor;