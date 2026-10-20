import React from 'react';
import { Calendar } from 'lucide-react';
import { Input, type InputProps } from '../Input';

export interface DateInputProps extends Omit<InputProps, 'type'> {}

export const DateInput = React.forwardRef<HTMLInputElement, DateInputProps>((props, ref) => {
  return (
    <Input
      ref={ref}
      type="date"
      leftIcon={<Calendar className="w-4 h-4 text-slate-400" />}
      {...props}
    />
  );
});

DateInput.displayName = 'DateInput';
