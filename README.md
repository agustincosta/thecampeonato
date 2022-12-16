# thecampeonato

OCR de facturas y análisis de datos

# Run commands and outputs for modules
1. Image preprocessing and OCR
```sh
  python Code/App.py $(imagePath)
```
- imagePath includes the whole directory route, filename and extension


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