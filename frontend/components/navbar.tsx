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
import React from "react";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";

const components: {
  option: string;
  value: { title: string; href: string; description: string; carry: boolean }[];
}[] = [
  {
    option: "Menu",
    value: [
      {
        title: "Generate New Project",
        href: "/gen",
        description: "Generate New Project Using Floor Plan",
        carry: false,
      },
      {
        title: "Dashboard",
        href: "/dashboard",
        description: "View the dashboard.",
        carry: true,
      },
      {
        title: "Sensors Catalog",
        href: "/shop",
        description:
          "View the sensors catalog, You can view sensor usage and order new sensors.",
        carry: false,
      },
    ],
  },
  {
    option: "Map",
    value: [
      {
        title: "Map",
        href: "/map",
        description: "View the map of the space.",
        carry: true,
      },
    ],
  },
];

export default function Navbar() {
  const { setTheme } = useTheme();
  const url = usePathname();

  const id = url.split("/")[2] || "";

  return (
    <nav className="flex items-center justify-between p-4 bg-background">
      <div className="text-xl font-bold">Logo</div>
      <div className="w-full h-full ml-10">
        <NavigationMenu className="w-full">
          <NavigationMenuList className="w-full">
            {components.map((component, index) => (
              <NavigationMenuItem key={index}>
                <NavigationMenuTrigger>
                  {component.option}
                </NavigationMenuTrigger>
                <NavigationMenuContent>
                  <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px] ">
                    {component.value.map((c) => (
                      <ListItem
                        key={c.title}
                        title={c.title}
                        href={c.carry ? `${c.href}/${id}` : c.href}
                      >
                        {c.description}
                      </ListItem>
                    ))}
                  </ul>
                </NavigationMenuContent>
              </NavigationMenuItem>
            ))}
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

const ListItem = React.forwardRef<
  React.ElementRef<"a">,
  React.ComponentPropsWithoutRef<"a">
>(({ className, title, children, ...props }, ref) => {
  return (
    <li>
      <NavigationMenuLink asChild>
        <a
          ref={ref}
          className={cn(
            "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
            className
          )}
          {...props}
        >
          <div className="text-sm font-medium leading-none">{title}</div>
          <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
            {children}
          </p>
        </a>
      </NavigationMenuLink>
    </li>
  );
});
ListItem.displayName = "ListItem";
