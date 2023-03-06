# Axione test

To run the project you can use the Dockerfile at the root of the project. You will need docker installed on your computer.
After that you can run the following commands:

```shell
$ docker build -t axione .
# this will run the project on port 8000, feel free to change it to your liking
$ docker run -dp 8000:8000 axione
```

## Limitations

There are some caveats with the current implementation:

- When data of a particular city cannot be found, I just cancel the whole operation and return a 503 error
- Some cities like Paris 5e will not have a page to find global note, again I'm radical here and return a 503 error
