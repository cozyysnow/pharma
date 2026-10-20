import React from 'react';
import { Input, type InputProps } from '../Input';

export interface TextInputProps extends InputProps {}

export const TextInput = React.forwardRef<HTMLInputElement, TextInputProps>((props, ref) => {
  return <Input ref={ref} type="text" {...props} />;
});

TextInput.displayName = 'TextInput';
