# PyOPACK – Python OPACK parser and encoder

OPACK is a propriety encoding scheme from Apple, used in a variety of services like *Handoff*, *Universal-Clipboard* and *WiFi Password Sharing*.
OPACK can encode the following data types:

- `bool`
- `int`
- `float` *(not implemented)*
- `str`
- `bytes`
- `list`
- `dict`
- `date` *(not implemented)*
- `UUID` *(not implemented)*

## Disclaimer

This implementation is used for testing and research purposes only, and is **not designed for productive use.**

## Usage Examples

### Encoder

```python
decoded = {
  "key1": bytes(12),
  "key2": [1,2,3],
}
encoded = OPACK.encode(decoded)
```

### Decoder

```python
decoded = OPACK.decode(encoded)
```
