# Docker

# <span style="color:blue">Build ECR Image Locally Using Docker

From my personal and professional experience, I have encountered challenges when trying to access AWS resources while developing code locally within a Docker image. I have observed individuals resorting to copying their AWS credentials directly into the repository path where the Dockerfile is located and then incorporating those credentials into the Docker image. However, this approach poses security risks for several reasons.

Recently, I devised a safer solution. Instead of storing AWS credentials within the Docker image, I recommend mounting the path where your AWS credentials reside into Docker's home path during runtime. This approach ensures that the credentials are not embedded within the Docker image itself, reducing the potential exposure of sensitive information.

By adopting this method, you can securely access AWS resources during development within a Docker environment without compromising the integrity of your credentials.

## <span style="color:purple">Pre Setup

To ensure proper AWS credential setup, follow these steps:

* Confirm that your AWS credentials are correctly configured in the `~/.aws/` directory.

To install the AWS Command Line Interface (CLI) within a Docker environment, you have a few options:

* If you are using a Dockerfile, add a line to install the awscli directly.
* If your project uses a requirements.txt file to install pip libraries, include awscli as a dependency in the requirements.txt file.
* Alternatively, if the docker build process takes a long time when awscli is added to the requirements.txt, you can install it manually inside the Docker container. Once inside the container, run the command `pip install awscli`.

These steps ensure that the AWS CLI is properly installed within the Docker environment, allowing seamless interaction with AWS services.

## <span style="color:purple">Local Development Using Docker

To build a Docker image using the standard approach, execute the command:
```
docker build -t <image-name>:<tag> .
```
This assumes that you are in the folder where the Dockerfile resides.

If you need to build the Docker image from a location outside the folder where the Dockerfile is located, utilize the -f argument. For example:
```
docker build -t <image-name>:<tag> -f <path-to-Dockerfile> .
```
These commands enable the creation of Docker images for local development. The standard approach assumes that the Dockerfile is present in the current directory, while the second command allows you to specify the path to the Dockerfile if it is located outside the current folder.

### <span style="color:green">Docker with Volumn Mount, AWS credentials, and Environment Variable
To achieve live code editing within a Docker container and temporary AWS resource access, you can utilize the following Docker command:

```
docker run -it -v <path-on-local-machine>:<path-inside-docker> -v $HOME/.aws:<home-path-docker-image>/.aws/ --env-file <path-to-env-file> <docker-image-name>:latest /bin/bash
```

This command provides the following functionalities:

1. The `-v <path-on-local-machine>:<path-inside-docker>` option mounts the local content into the Docker image, allowing you to make code changes from your preferred IDE. Any modifications made to the files within the IDE will be automatically reflected inside the Docker container. This eliminates the need to rebuild the image each time you want to test code changes.

2. The `-v $HOME/.aws:<home-path>/.aws/` option mounts your AWS credentials into the Docker container, facilitating temporary access to AWS resources from within the container. This enables you to bypass the steps of uploading the image to ECR, triggering Batch jobs, and waiting for their completion to determine if your code is successful or not. By setting up this local environment, you can accelerate your development cycle and save time. Please note that you might need to replace `<home-path>` with the absolute home path by running the image once and determining the correct value.

3. The `--env-file <path-to-env-file>` option allows you to set up runtime environment variables, similar to how you would configure them when running a Batch job. Create a file named `[name].env`, such as `batch.env`, and define all the required environment variables along with their corresponding values. For example:
    ```
    XTCE_SCHEMA_S3_PATH=L0_data_products/sci_packet_xtce_schema.xml
    DYNAMODB_TABLE_NAME=ProcessingEvents
    OUTPUT_FILE_PREFIX=tenzin_test
    ```
    These variables can be passed into the Batch job during runtime.

This Docker command provides a convenient way to edit code live, access AWS resources within the container, and configure necessary environment variables for smooth development and testing.

## <span style="color:purple">Docker-Compose Approach
We can enhance and simplify the aforementioned approach by incorporating Docker Compose. By utilizing Docker Compose, the setup of AWS credentials becomes more streamlined.

Here is an example of the contents of a docker-compose.yml file:
```
version: "3.9"
services:
  imap_processing_cdk:
    build:
      context: ./<some-path-name>
      dockerfile: . # path to Dockerfile
    image: imap_processing_workspace
    stdin_open: true # This line is same as docker run -i
    tty: true # This line is same as docker run -t
    volumes: # mount volumes
      - ./:/workspaces/cdk-workspace/
      - $HOME/.aws:/workspaces/cdk-workspace/.aws/
    environment:
      - AWS_PROFILE=$AWS_PROFILE
      - AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
      - AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
      - AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
    env_file: # Set environment variables using .env file
      - ./<some-path>/batch.env
```

To build the image, execute the following command:
```
docker-compose build <service-name>
```

To run an interactive Docker container locally, use this command:
```
docker-compose run <service-name> /bin/bash
```

### <span style="color:green"> Build Context Explanation </span>

If the Dockerfile is being built with files located within the same directory, there is no need to set context and dockerfile. Instead, simply set build to the path where the Dockerfile resides.

If files are being copied from a different folder outside of where the Dockerfile is located, you can build the Docker images using either of the following methods:

1. Create the docker-compose.yml file in the same path where the Dockerfile exists.
2. Create the docker-compose.yml file in the same directory level as the folder from which the files are being copied.

In the first case, we define the build location for Docker using the following syntax. The "context" parameter keeps track of the directory path, while the "dockerfile" parameter specifies the exact path to the Dockerfile.

In this particular case, the context is set to `./../../../../`. The context path starts from the directory where the docker-compose.yml file is located. By setting it to `./../../../../`, we are instructing it to start from the path of the docker-compose.yml file and navigate four directories up to reach the desired directory.

Once we have changed the build directory by setting the context value, we specify the path to the Dockerfile using the "dockerfile" parameter. The "dockerfile" value is set to the path where the Dockerfile exists.

Eg.

```
version: "3.9"
services:
  service_name:
    build:
      context: ./../../../../
      dockerfile: src/processing/batch/some_job/Dockerfile
    image: image_name
    stdin_open: true # This line is same as docker run -i
    tty: true # This line is same as docker run -t
    volumes: # mount volumes
      - ./:/src/
      - $HOME/.aws:/root/.aws/
    env_file: # Set environment variables using .env file
      - batch.env
```


In the second case, we place the docker-compose.yml file in the same folder as the directory from which we are copying files. Then, we set the context to `.` which represents the current directory. By doing so, we indicate that we want to start the build process from the current directory.

Next, we specify the path to the Dockerfile using the "dockerfile" parameter. The "dockerfile" value is set to the location where the Dockerfile exists, allowing Docker to find and use the specified Dockerfile for building the container.

Eg.

```
version: "3.9"
services:
  service_name:
    build:
      context: .
      dockerfile: src/processing/batch/some_job/Dockerfile
    image: pixel_binning # docker image name
    stdin_open: true # This line is same as docker run -i
    tty: true # This line is same as docker run -t
    volumes: # mount volumes
      - ./:/var/task/
      - $HOME/.aws:/root/.aws/
    env_file: # Set environment variables using .env file
      - l1a_env.env
```


## <span style="color:purple">Steps to test AWS Lambda Image locally

1. Build image same standard way
2. Run lambda image using this command (with value changed as needed)
    ```
    docker run -p 9000:8080 -v $HOME/.aws:/root/.aws/ --env-file aws_env.env <image-name>
    ```
3. To invoke the lambda image, run this curl command (with event input value as needed)
    ```
    curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"Bucket": "sth", ..., "otherKey": "otherValue"}'
    ```
