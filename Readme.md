# How to use this folder
This ReadMe is a guide to using this code effectively locally.


```bash
pyinstaller app.py --onedir --windowed --icon=myicon.ico  # Windows
pyinstaller app.py --onedir --windowed --icon=myicon.icns  # macOS

```

## MacOs/Linux

```bash

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

pyinstaller app.py --onedir --windowed --icon=myicon.icns  # macOS
```



## Windows

```PS

py -m venv .venv

.\.venv\Scripts\activate

py -m pip install -r requirements.txt

pyinstaller app.py --onedir --windowed --icon=myicon.ico  # Windows
```


