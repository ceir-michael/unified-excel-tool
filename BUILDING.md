# Building Unified Excel Tools

PyInstaller must run on the target operating system. The generated application
includes Python and all runtime dependencies; end users do not need to install
Python, CustomTkinter, Microsoft Excel, or any Python packages.

## Windows

Run:

```bat
build\build_windows.bat
```

The script creates and uses an isolated `.build-venv`, installs the pinned build
dependencies, and produces the self-contained application folder at:

```text
dist\UnifiedExcelTools\
```

For the recommended single-file installer, install Inno Setup 6 on the build
computer and run the same script again. It will also produce:

```text
dist\installer\UnifiedExcelTools-<version>-Setup.exe
```

The installer creates Start menu and optional desktop shortcuts and includes an
uninstaller. Inno Setup is needed only on the build computer, not by end users.

Before publishing a release, test the installer with Windows Sandbox or another
clean Windows machine. Code-signing the installer and application executable is
also recommended for public distribution.

## Linux

```bash
bash build/build_linux.sh
```

## macOS

```bash
bash build/build_macos.sh
```

The GitHub Actions workflow also creates cross-platform build artifacts. GitLab
CI provides equivalent jobs; its Windows and macOS jobs require runners tagged
`windows` and `macos`. GitLab artifacts are retained for 30 days.
