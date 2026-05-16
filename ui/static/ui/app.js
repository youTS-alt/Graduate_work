document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-tabs]').forEach((tabsRoot) => {
    const buttons = tabsRoot.querySelectorAll('[data-tab-target]');
    const panels = tabsRoot.querySelectorAll('[data-tab-panel]');

    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        const target = button.dataset.tabTarget;

        buttons.forEach((item) => item.classList.toggle('active', item === button));
        panels.forEach((panel) => {
          panel.classList.toggle('active', panel.dataset.tabPanel === target);
        });
      });
    });
  });
});
