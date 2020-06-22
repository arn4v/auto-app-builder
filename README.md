# **Auto App Builder**

---

## Parameter and usage overview:

- Building app:
  `python build.py --build <app-name>`
- Build all apps:
  `python build.py --build-all`
- Build without signing:
  `python build.py --build <app-name> --no-sign`
- Adding apps to JSON:
  `python build.py -a <repository-url>`
- Adding a list of apps from a file:
  - Save repository URL to \*.txt in the following format:
  ```
  https://github.com/TeamNewPipe/NewPipe
  https://github.com/SimpleMobileTools/Simple-Gallery
  ```
  - Run `python build.py --from-file <file-name>`
- Delete apps from JSON:
  `python build.py --remove <app-name>`
- List apps in JSON:
  `python build.py --list`
- Clean OUT dir:
  `python build.py --clean`