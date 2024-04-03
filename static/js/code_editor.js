

const editor = document.getElementById("editor");
const code = CodeMirror(editor, {
  value: "hello\n",
  mode: "yaml",
  lineNumbers: true,
  gutters: ["CodeMirror-lint-markers"],
  lint: true
});

code.on("change", function () {
  const content = code.getValue();
  try {
    const _yaml = jsyaml.loadAll(content);
    console.log(_yaml);
  } catch (e) {
    console.log(e);
  }
});
