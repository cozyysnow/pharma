import React from 'react';
import { Input, type InputProps } from '../Input';
import { cn } from '../../../utils/cn';

export interface NumberInputProps extends Omit<InputProps, 'type'> {
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
}

export const NumberInput = React.forwardRef<HTMLInputElement, NumberInputProps>(
  ({ unit, className, ...props }, ref) => {
    return (
      <Input
        ref={ref}
        type="number"
        className={cn('tabular-nums font-mono', className)}
        rightIcon={unit ? <span className="text-xs font-sans text-slate-500">{unit}</span> : undefined}
        {...props}
      />
    );
  }
);

NumberInput.displayName = 'NumberInput';
