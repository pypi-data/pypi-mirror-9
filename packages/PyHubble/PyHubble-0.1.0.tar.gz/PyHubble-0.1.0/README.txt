# Pyhubble

Python client for [hubble](https://github.com/jaymedavis/hubble), the terminal dashboard

    pip install pyhubble


## Usage

Import the client

```python
    from pyhubble import Hubble
```

Initialization and sending values

```python
    hubble = Hubble('http://localhost:9999/')
    hubble.send({'label': 'Test', 'value': 1, 'column': 0})
```

Increment/decrement a label

```python
    hubble.increment('Test')  # Increments the value of this label
    hubble.decrement('Test')  # Decrements the value of this label
```


## TODO

Poll implementation
Unittest
High, low and screen properties
