"use strict";

{
  const root = document.documentElement;

  function setTheme(theme) {
    root.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }

  const savedTheme = localStorage.getItem("theme");
  const initialTheme =
    savedTheme === "light" || savedTheme === "dark"
      ? savedTheme
      : window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";

  setTheme(initialTheme);

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".theme-toggle").forEach((button) => {
      button.addEventListener("click", () => {
        setTheme(root.dataset.theme === "dark" ? "light" : "dark");
      });
    });
  });
}