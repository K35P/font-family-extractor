# Font Family Extractor

A small command-line utility that reads a **variable font** (TrueType or OpenType with an `fvar` table) and exports **one static font file per named instance** defined in that table. Output files are written to a directory named after the source font file (without extension), placed next to the input by default.

## Features

- Enumerates all predefined instances from the OpenType `fvar` table
- Produces static `.ttf` files for variable TTF inputs, or static `.otf` for variable OTF inputs
- Sanitizes instance names for safe filenames and avoids collisions with numeric suffixes (`_2`, `_3`, …)
- Reloads the source font for each instance so [fontTools](https://github.com/fonttools/fonttools) instantiation does not corrupt shared state

## Requirements

- **Python** 3.10 or newer (the script uses only the standard library plus fontTools)
- **fontTools** 4.50 or newer (see [`requirements.txt`](requirements.txt))

Supported input extensions are **`.ttf`** and **`.otf`**. TrueType Collection (`.ttc`) files are not supported.

## Installation

```bash
git clone https://github.com/K35P/font-family-extractor.git
cd font-family-extractor
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python extract.py path/to/YourVariableFont.ttf
python extract.py path/to/YourVariableFont.otf
```

This creates `path/to/YourVariableFont/` (same base name as the file, no extension) and writes one static font per named instance. Use `python extract.py -h` for options.

### Custom output directory

To write files to an explicit folder instead:

```bash
python extract.py path/to/YourVariableFont.ttf --output-dir /absolute/or/relative/target/dir
```

The target directory is created if it does not exist.

### Example

```text
fonts/
  MyFamily-VF.ttf
```

After:

```bash
python extract.py fonts/MyFamily-VF.ttf
```

```text
fonts/
  MyFamily-VF.ttf
  MyFamily-VF/
    Regular.ttf
    Bold.ttf
    Light_Italic.ttf
    ...
```

## How instance filenames are chosen

Each instance uses its **subfamily name** from the font’s `name` table (via `subfamilyNameID` in `fvar`). If that name ID cannot be resolved, the file is named `instance_<id>`. Spaces are replaced with underscores, characters that are invalid in file names are replaced, and leading or trailing dots or spaces are stripped. If two instances would map to the same filename, a numeric suffix is appended.

## Limitations

- Only fonts that expose a non-empty set of **named instances** in `fvar` are supported. Axes-only variable fonts with no predefined instances will exit with an error.
- The tool does not synthesize intermediate weights or widths; it only exports what the font author registered as instances.
- **Invalid or unreadable** font files (or non-font data) are reported with a short error message and a non-zero exit code; the script does not print a Python traceback for typical fontTools read errors.
- Ensure you have the **legal right** to process and redistribute the fonts you use; this repository only provides the extraction script.

## License

This project’s **source code** is released under the [MIT License](LICENSE).

Fonts you process remain subject to their own licenses. This tool does not grant any rights to third-party typefaces.

## Contributing

Issues and pull requests are welcome. Please keep code comments and documentation in English.
