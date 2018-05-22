# nanoView
> Data Visualization tool for nanopore sequencing data.

![](cover.png)


## Prerequisites

- NPM & NodeJS.
  - Standard NodeJS executable is named as nodejs, which needs to be
  linked to another file named node which is recognized by this program. It can be
  done using the command `ln -s /path/to/nodejs /path/to/node`.

## Installation

```sh
$ git clone https://github.com/coadunate/nanoView.git
$ cd nanoView
$ npm install
$ npm run build
```
## Deployment

- Before running the application, the API needs to be deployed which generates the data for the visualization. Make sure that you are in nanoView directory.

```sh
$ python3 ./nanopore-api/app.py
```

- Run the following command to serve the application on `http-server`

```sh
$ npm run http-server
```
Then open http://127.0.0.1:8080/examples/ in your browser of choice (preferably Chrome).


## API

Write about the function of API in this program and how it can be used.
