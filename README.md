# thecampeonato

OCR de facturas y análisis de datos

![Diagrama funcional](https://github.com/agustincosta/thecampeonato/blob/main/tutorial/diagrama_funcional.png)

# Local development with docker

1. Build the docker image:
```sh
docker build -t myapp-dev .
```
2. Run the container:
  ```sh
  docker run -it --name myapp --rm \
      --volume $(pwd):/usr/src/app \
      --net=host myapp-dev:latest \
      sh
  ```

## Run linters locally

1. Run flake8 linter:
```sh
flake8
```

## Run tests locally

1. Run pytest:
```sh
pytest Code/tests/
```