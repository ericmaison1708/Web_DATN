document.addEventListener("DOMContentLoaded", function () {
  // === XỬ LÝ CUỘN MENU ===

  // Trang chủ
  const scrollBtn = document.getElementById("scrollToTop");
  if (scrollBtn) {
    scrollBtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // Giới thiệu
  const aboutBtn = document.getElementById("goToAbout");
  const aboutSection = document.getElementById("about");
  if (aboutBtn && aboutSection) {
    aboutBtn.addEventListener("click", function (e) {
      e.preventDefault();
      aboutSection.scrollIntoView({ behavior: "smooth" });
    });
  }

  // Hướng dẫn
  const guideBtn = document.getElementById("goToGuide");
  const guideSection = document.getElementById("guide");
  if (guideBtn && guideSection) {
    guideBtn.addEventListener("click", function (e) {
      e.preventDefault();
      guideSection.scrollIntoView({ behavior: "smooth" });
    });
  }

  // === XỬ LÝ CÂU HỎI / DOT SLIDER ===

  const questionList = document.querySelector(".question-list");
  const questionItems = document.querySelectorAll(".question-item");
  const questionContainer = document.querySelector(".question");
  const dots = document.querySelectorAll(".question .dot");

  function updateQuestionHeight(index) {
    const item = questionItems[index];
    if (item && questionContainer) {
      const newHeight = item.offsetHeight;
      questionContainer.style.height = `${newHeight}px`;
    }
  }

  dots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      questionList.style.transform = `translateX(-${index * 100}%)`;

      dots.forEach((d) => d.classList.remove("active"));
      dot.classList.add("active");

      updateQuestionHeight(index);
    });
  });

  // Thiết lập chiều cao lần đầu khi trang load
  updateQuestionHeight(0);
});

document.addEventListener("DOMContentLoaded", function () {
  const guideBtn = document.getElementById("btnScrollToGuide");
  const guideSection = document.getElementById("guide");

  if (guideBtn && guideSection) {
    guideBtn.addEventListener("click", function (e) {
      e.preventDefault();
      guideSection.scrollIntoView({
        behavior: "smooth",
      });
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const questionList = document.querySelector(".question-list");
  const questionItems = document.querySelectorAll(".question-item");
  const dots = document.querySelectorAll(".dots .dot");

  function updateQuestionHeight(index) {
    const container = document.querySelector(".question");
    const height = questionItems[index].offsetHeight;
    container.style.height = `${height}px`;
  }

  dots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      // slide
      questionList.style.transform = `translateX(-${index * 100}%)`;

      // update active dot
      dots.forEach((d) => d.classList.remove("active"));
      dot.classList.add("active");

      // auto height
      updateQuestionHeight(index);
    });
  });

  updateQuestionHeight(0);
});
