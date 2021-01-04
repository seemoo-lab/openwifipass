# PyOPACK - Python OPACK parser and encoder

> This implementation is used for testing and research purposes only, and is **not designed for productive use.**

OPACK is a propriety encoding scheme from Apple, used in a variety of services like *Handoff*, *Universal-Clipboard* and *WiFi Password Sharing*.

OPACK can encode the following data types:

- bool
- int
- float
- str
- bytes
- list
- dict
- date (not implemented)
- UUID (not implemented)

## Encoder

```python
payload = {
  "key1": bytes(12),
  "key2": [1,2,3],
  "key3": 3.4
}
opackData = OPACK.encode(payload)
print(opackData)
```

## Decoder

```python
payload_decoded = OPACK.decode(opackData)
print(payload_decoded)
```

## License

Copyright 2020 Jannik Lorenz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
