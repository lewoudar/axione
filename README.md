# Axione test

There are two versions of this project: one on the main branch and one on the *enhancement* branch. Read the *limitations*
section for more information;

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
- If you don't want this behaviour, switch to the *enhancement* branch. Here I remove cities where I can find city data
  and those that don't have note defaults with a note of **-1**
