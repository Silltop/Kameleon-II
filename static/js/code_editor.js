

const editor = document.getElementById("editor");
let code_data = document.getElementById("editor-content");
const code = CodeMirror(editor, {
  value: code_data.innerHTML,
  mode: "yaml",
  lineNumbers: true,
  gutters: ["CodeMirror-lint-markers"],
  lint: true
});

if (halfmoon.readCookie("halfmoon_preferredMode")) {
    if (halfmoon.readCookie("halfmoon_preferredMode") == "light-mode") {
        code.setOption("theme", "3024-day");
    }
    else if (halfmoon.readCookie("halfmoon_preferredMode") == "dark-mode") {
        code.setOption("theme", "blackboard");
    }
}

code.on("change", function () {
  const content = code.getValue();
  try {
    const _yaml = jsyaml.loadAll(content);
    console.log(_yaml);
  } catch (e) {
    console.log(e);
  }
});
