(() => {
  function getCookie(name) {
    const cookieValue = document.cookie
      .split(";")
      .map((c) => c.trim())
      .find((c) => c.startsWith(name + "="));
    if (!cookieValue) return "";
    return decodeURIComponent(cookieValue.split("=", 2)[1] || "");
  }

  function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function captureAndSend() {
    const urlPath = window.location.pathname || "/";
    const key = `auto_screenshot_sent:${urlPath}${window.location.search || ""}`;
    const inProgressKey = `auto_screenshot_in_progress:${urlPath}${window.location.search || ""}`;

    if (sessionStorage.getItem(key) === "1" || sessionStorage.getItem(inProgressKey) === "1") {
      return;
    }
    sessionStorage.setItem(inProgressKey, "1");

    try {
      if (typeof window.html2canvas !== "function") {
        throw new Error("html2canvas не подключён");
      }

      await delay(800);

      const canvas = await window.html2canvas(document.body, {
        backgroundColor: "#ffffff",
        scale: 1.5,
        useCORS: true,
        scrollX: 0,
        scrollY: -window.scrollY,
        windowWidth: document.documentElement.scrollWidth,
        windowHeight: document.documentElement.scrollHeight,
      });

      const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
      if (!blob) {
        throw new Error("Не удалось сформировать PNG");
      }

      const formData = new FormData();
      formData.append("image", blob, "page.png");
      formData.append("url_path", urlPath);

      const csrfToken = getCookie("csrftoken");
      const resp = await fetch("/system/save-page-screenshot/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        body: formData,
      });

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }

      const data = await resp.json().catch(() => null);
      if (!data || data.ok !== true) {
        throw new Error("Backend вернул ошибку");
      }

      sessionStorage.setItem(key, "1");
    } catch (e) {
      // Не ломаем страницу из-за скриншотов.
      // При необходимости можно добавить логирование в консоль:
      // console.debug("[auto screenshot]", e);
    } finally {
      sessionStorage.removeItem(inProgressKey);
    }
  }

  window.addEventListener("pageshow", () => {
    captureAndSend();
  });
})();

