# Building Unified Excel Tools

Windows:
`build\\build_windows.bat`

Linux:
`bash build/build_linux.sh`

macOS:
`bash build/build_macos.sh`

Note: PyInstaller must run on the target operating system.
Use GitHub Actions workflow for automatic cross-platform builds.

All platform scripts run the test suite, create a one-directory application, and execute a non-visual startup smoke test. GitHub Actions packages native archives for all three platforms and publishes them when a `v*` tag is pushed. Tags with a prerelease suffix such as `-beta.1` create GitHub prereleases.

GitLab CI also provides cross-platform jobs in `.gitlab-ci.yml`. The Linux job
uses GitLab's Docker runner. The Windows and macOS jobs require GitLab runners
tagged `windows` and `macos`, respectively. Build artifacts are retained for 30
days.
