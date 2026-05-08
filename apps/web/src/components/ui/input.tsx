import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg border border-[hsl(var(--guardian-border))] bg-[hsl(var(--guardian-bg-secondary))] px-3 py-2 text-sm text-[hsl(var(--guardian-text-primary))] placeholder:text-[hsl(var(--guardian-text-muted))] input-glow transition-all duration-200 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-[hsl(var(--guardian-text-secondary))]",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };