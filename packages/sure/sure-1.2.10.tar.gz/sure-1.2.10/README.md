# sure `1.2.10`

A testing library for python with powerful and flexible assertions. Sure is heavily inspired by [should.js](https://github.com/visionmedia/should.js/)

[![Build Status](https://travis-ci.org/gabrielfalcao/sure.png?branch=master)](https://travis-ci.org/gabrielfalcao/sure)

# Installing

    user@machine:~$ [sudo] pip install sure


# Documentation

Available in the [website](http://falcao.it/sure) or under the `spec` directory.

You can also build the documentation locally using markment:

```bash
pip install markment
markment --server --theme=rtd ./spec/
```


## Here is a tease

### Equality

#### (number).should.equal(number)

```python
import sure

(4).should.be.equal(2 + 2)
(7.5).should.eql(3.5 + 4)
(2).should.equal(8 / 4)

(3).shouldnt.be.equal(5)
```

#### {'a': 'collection'}.should.equal({'a': 'collection'}) does deep comparison

```python
{'foo': 'bar'}.should.equal({'foo': 'bar'})
{'foo': 'bar'}.should.eql({'foo': 'bar'})
{'foo': 'bar'}.must.be.equal({'foo': 'bar'})

```

#### "A string".lower().should.equal("a string") also works

```python
"Awesome ASSERTIONS".lower().split().should.equal(['awesome', 'assertions'])
```
