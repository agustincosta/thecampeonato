# thecampeonato

OCR de facturas y análisis de datos

# Run commands and outputs for modules
1. Image preprocessing and OCR
```sh
  python App.py $(imagePath) $(resultDirPath) $(resultFilename)
```
The imagePath parameter includes the whole directory route, filename and extension
resultDirPath must be just the directory path to which the resulting image and text file are written
resultFilename must be an identifying filename for the result files, without directory path or extension. In both cases the final filenames will include the 'binarized' and 'OCR' prefixes as well as the extensions '.jpg' and '.txt'

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