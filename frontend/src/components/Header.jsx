import { Sparkles, Menu, User } from "lucide-react";
import { Button } from "./Button";

export function Header({ onMenuToggle }) {
  return (
    <header className="bg-white/80 backdrop-blur-lg border-b border-border sticky top-0 z-50">
      <div className="container mx-auto px-4 py-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/logo.png"
              alt="FoodScan AI Logo"
              className="h-20 w-auto object-contain"
            />
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={onMenuToggle}>
              <Menu className="size-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <User className="size-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
