function updateLogo() {
  const isDark = document.documentElement.classList.contains("dark");
  const logo = document.querySelector("img");

  if (!logo) return;

  if (isDark) {
    logo.src = "http://localhost:8000/public/logo_dark.png";
  } else {
    logo.src = "http://localhost:8000/public/logo_dark.png";
  }
}

setInterval(updateLogo, 500);