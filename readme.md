# Python API

## About

A Python package of common EDI functions including:
- Logging 
- oData connection settings
- Serialisation
- web handlers

## Install
To install this package use
```
pip install MedatechUK.APY
```

## Imports

### Log Class

```python
from MedatechUK.mLog import mLog
```
See: [Logging Class](log.md "Logging Class")

### Config Class

```python
from MedatechUK.oDataConfig import Config
```
See: [oData Configuration](oDataConfig.md "oData Configuration")

### Serial Class

```python
from MedatechUK.Serial import SerialBase , SerialT , SerialF
```
See: [How to create a serial object](serial.md "How to create a serial object")

See: [Serial object methods](serialmethod.md "Serial object methods")

### APY Class

```python
from MedatechUK.apy import Request , Response
```
See: [How to set up IIS](iis.md "How to set up IIS")

See: [Creating web handlers](apy.md "Creating web handlers")
