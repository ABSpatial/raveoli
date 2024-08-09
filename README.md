# raveoli
Raster and vector tile server, all-in-one

## Install and run



```
git clone https://github.com/ABSpatial/raveoli.git
```

```
cd raveoli
```


```
docker build . -t raveoli
```


```
docker run -it --rm -p 8000:8000 --name raveoli-conteiner raveoli
```

Raveoli server working on:
[http://localhost:8000/](http://localhost:8000/)

API documentation:
[http://localhost:8000/docs](http://localhost:8000/docs)