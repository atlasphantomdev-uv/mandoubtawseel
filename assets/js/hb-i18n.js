window.addEventListener("DOMContentLoaded", () => {
  // Toggle language chooser sub-menu
  const languageChoosers = document.querySelectorAll("[data-hb-language-chooser]");
  languageChoosers.forEach((languageChooser) => {
    languageChooser.addEventListener("click", (e) => {
      e.preventDefault();
      languageChooser.dataset.state = languageChooser.dataset.state === "open" ? "closed" : "open";
      const languageOptions = languageChooser.nextElementSibling;
      languageOptions.classList.toggle("hidden");
      const languageChooserRect = languageChooser.getBoundingClientRect();
      const translateY = languageChooserRect.bottom - window.innerHeight + 40;
      // Anchor to the trailing inline edge: RTL pages measure from the right edge.
      const isRTL = getComputedStyle(document.documentElement).direction === "rtl";
      const optionsWidth = Math.max(languageChooserRect.width, 50);
      const translateX = isRTL ? languageChooserRect.right - optionsWidth : languageChooserRect.left;
      languageOptions.style.transform = `translate3d(${translateX}px, ${translateY}px, 0)`;
      languageOptions.style.minWidth = `${optionsWidth}px`;
    });
  });

  // Handle clicks outside chooser
  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-hb-language-chooser]") === null) {
      languageChoosers.forEach((languageChooser) => {
        languageChooser.dataset.state = "closed";
        const languageOptions = languageChooser.nextElementSibling;
        languageOptions.classList.add("hidden");
      });
    }
  });
});
