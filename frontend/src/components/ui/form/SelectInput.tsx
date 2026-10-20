import React from 'react';
import { Select, type SelectProps } from '../Select';

export interface SelectInputProps extends SelectProps {}

export const SelectInput = React.forwardRef<HTMLSelectElement, SelectInputProps>((props, ref) => {
  return <Select ref={ref} {...props} />;
});

SelectInput.displayName = 'SelectInput';
