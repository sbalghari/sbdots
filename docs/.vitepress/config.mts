import { defineConfig } from "vitepress";

export default defineConfig({
  title: "SBDots - Hyprland",
  description: "A dynamic, feature-rich and polished dotfiles for hyprland.",
  lastUpdated: true,
  cleanUrls: true,
  lang: "en-US",

  head: [["link", { rel: "icon", href: "logo_dark.svg" }]],

  markdown: {
    theme: {
      light: "catppuccin-latte",
      dark: "catppuccin-mocha",
    },
  },

  themeConfig: {
    siteTitle: "SBDots",
    logo: {
      dark: "/logo_dark.svg",
      light: "/logo_light.svg",
    },

    nav: [
      { text: "Home", link: "/" },
      {
        text: "Screenshots",
        link: "/pages/screenshots",
        activeMatch: "/screenshots",
      },
      {
        text: "Wiki",
        link: "/getting_started/overview",
        activeMatch: "/(getting_started|configurations|help|credits)/",
      },
      {
        text: "v0.0.3-alpha",
        items: [
          {
            text: "Changelog",
            link: "https://github.com/sbalghari/sbdots/blob/main/CHANGELOG.md",
          },
          {
            text: "Contributing",
            link: "https://github.com/sbalghari/sbdots/blob/main/CONTRIBUTING.md",
          },
          {
            text: "License",
            link: "https://github.com/sbalghari/sbdots/blob/main/LICENSE.md",
          },
        ],
      },
    ],

    sidebar: [
      {
        text: "Menu",
        items: [
          {
            text: "Getting Started",
            items: [
              { text: "Overview", link: "/getting_started/overview" },
              { text: "Installation", link: "/getting_started/installation" },
              { text: "Packages", link: "/getting_started/packages" },
              { text: "Updates", link: "/getting_started/updates" },
              {
                text: "Uninstallation",
                link: "/getting_started/uninstallation",
              },
            ],
          },
          {
            text: "Configurations",
            items: [
              { text: "Key Bindings", link: "/configurations/keybinds" },
              { text: "Hyprland Config", link: "/configurations/hyprland" },
              { text: "GTK-3/4 Theming", link: "/configurations/gtk_theming" },
              { text: "Status Bar", link: "/configurations/waybar" },
              { text: "Notifications", link: "/configurations/notifications" },
              { text: "Launchers", link: "/configurations/launcher" },
            ],
          },
          {
            text: "Help",
            items: [
              { text: "Troubleshooting", link: "/help/troubleshooting" },
              { text: "FAQs", link: "/help/faqs" },
            ],
          },
          {
            text: "Credits",
            items: [{ text: "Thanks", link: "/credits/thanks" }],
          },
        ],
      },
    ],

    socialLinks: [
      { icon: "github", link: "https://github.com/sbalghari/sbdots" },
    ],

    editLink: {
      pattern: "https://github.com/sbalghari/sbdots/tree/main/docs/:path",
      text: "Edit this page on GitHub",
    },

    search: {
      provider: "local",
    },

    footer: {
      message:
        "<div class='footer-message'> Released under the GNU GPL-3.0 License. </div>",
      copyright:
        "<div class='footer-copyright'> Copyright © 2024 Saifullah Balghari. </div>",
    },
  },
});
