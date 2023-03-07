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

- When data of a particular city cannot be found, I removed it from the results
- Some cities like Paris 5e don't have a page to find global note, I just return -1 
