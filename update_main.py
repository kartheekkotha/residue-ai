with open("residue/__main__.py", "r") as f:
    code = f.read()

code = code.replace(
    "from residue.installer.platforms import claude, gemini, cursor",
    "from residue.installer.platforms import claude, gemini, cursor, codex"
)

if "elif p == \"codex\":" not in code:
    code = code.replace(
        "            elif p == \"cursor\":\n                actions = cursor.install()",
        "            elif p == \"cursor\":\n                actions = cursor.install()\n            elif p == \"codex\":\n                actions = codex.install()"
    )

with open("residue/__main__.py", "w") as f:
    f.write(code)
