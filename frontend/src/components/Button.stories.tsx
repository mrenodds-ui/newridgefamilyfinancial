import type { Meta, StoryObj } from "@storybook/react";
import type React from "react";

import "./Button.stories.css";

type ButtonProps = Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "style">;

const Button = ({ children, className, ...props }: ButtonProps) => (
  <button {...props} className={className ? `button-story__button ${className}` : "button-story__button"}>
    {children}
  </button>
);

const meta: Meta<typeof Button> = {
  title: "Components/Button",
  component: Button,
  tags: ["autodocs"],
};
export default meta;

type Story = StoryObj<typeof Button>;

export const Default: Story = {
  args: {
    children: "Button",
  },
};

export const Disabled: Story = {
  args: {
    children: "Disabled",
    disabled: true,
  },
};
