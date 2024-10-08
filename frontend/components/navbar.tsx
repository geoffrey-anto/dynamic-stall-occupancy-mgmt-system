"use client";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Moon, Sun, User } from "lucide-react";
import { useTheme } from "next-themes";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import Link from "next/link";

export default function Navbar() {
  const { setTheme } = useTheme();

  return (
    <nav className="flex items-center justify-between p-4 bg-background">
      <div className="text-xl font-bold">Logo</div>
      <div className="w-full h-full ml-10">
        <NavigationMenu className="w-full">
          <NavigationMenuList className="w-full">
            <NavigationMenuItem className="w-full">
              <NavigationMenuTrigger>View Map</NavigationMenuTrigger>
              <NavigationMenuContent className="w-full">
                <NavigationMenuLink className="w-full">
                  <Link href="/map">Map</Link>
                </NavigationMenuLink>
              </NavigationMenuContent>
            </NavigationMenuItem>
            <NavigationMenuItem className="w-full">
              <NavigationMenuTrigger className="w-full">
                Dashboard
              </NavigationMenuTrigger>
              <NavigationMenuContent className="w-full">
                <NavigationMenuLink className="w-full">
                  <Link href="/dashboard">Dashboard</Link>
                </NavigationMenuLink>
              </NavigationMenuContent>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      </div>

      <div className="flex items-center space-x-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setTheme("light")}>
              Light
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("dark")}>
              Dark
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme("system")}>
              System
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <Button variant="ghost" size="icon">
          <User className="h-[1.2rem] w-[1.2rem]" />
          <span className="sr-only">User menu</span>
        </Button>
      </div>
    </nav>
  );
}
