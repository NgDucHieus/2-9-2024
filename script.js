const flagEl = document.getElementById("flag");

const rows = 50;
const columns = 75;

const generateUnit = (columnNum) => {
  const flagUnit = document.createElement("div");
  flagUnit.classList.add("flag-unit");
  flagUnit.style.setProperty("animation-delay", `${columnNum * 10}ms`);
  flagUnit.style.setProperty("--displacement", `${columnNum / 4}px`);

  const column = document.getElementById(`column-${columnNum}`);
  column.innerHTML += flagUnit.outerHTML;
};

for (let i = 0; i < columns; i++) {
  flagEl.innerHTML += `<div class="column" id="column-${i}"></div>`;
  for (let j = 0; j < rows; j++) {
    generateUnit(i);
  }
}
