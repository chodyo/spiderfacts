# spiderfacts

#### Slack bot that blurts out spider facts when a key word is triggered. Bot based on (mattmakai's work)[https://github.com/mattmakai/slack-starterbot]

## Installation necessities

1.  Create `spiderfacts` bot on your (slack team)[https://slack.com/apps/new/A0F7YS25R-bots].
1.  Place the bot into whatever channels you wish it to be a member of.
1.  Copy the API token into the `SPIDER_FACTS_TOKEN` environment variable on the machine where the code will run.
1.  Run `spiderfacts.py` whenever you want your bot to be active.

## Docker & AWS

#### From [AWS Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html)

### Docker

1.  `docker build -t spiderfacts .` => Builds Docker image.
    * `Dockerfile` must be created before the command will run
1.  `docker images --filter reference=spiderfacts` => Confirm image was made
1.  `docker run -e docker run -e SPIDER_FACTS_TOKEN=xoxb-############-######################## spiderfacts` => Run the program in Docker. Note, this will continue running until it is manually stopped. Running this command repeatedly _will_ run multiple spiderfacts instances.
    * populate the hashes with the slack API token

### [AWS ECR](https://us-west-2.console.aws.amazon.com/ecs/home?region=us-west-2#/repositories)

1.  `aws ecr create-repository --repository-name spiderfacts`
1.  `docker tag spiderfacts aws_account_id.dkr.ecr.region.amazonaws.com/spiderfacts`
    * `aws_account_id` must be replaced with the `registryId` provided in the previous command.
    * `region` must be replaced with whatever region is being used.
1.  `aws ecr get-login --no-include-email` => get the docker login authentication command string for your registry
    * Provides an authorization token that is valid for 12 hours. It's just a big command that needs to be entered. Read the AWS Guide link posted above for more info, especially about using authentication from unsecured computers.
1.  `docker push aws_account_id.dkr.ecr.us-west-2.amazonaws.com/spiderfacts` => Docker image is now sitting on AWS.

### [AWS Task Definition](https://us-west-2.console.aws.amazon.com/ecs/home?region=us-west-2#/taskDefinitions)

1.  Create a file called `spiderfacts-task-def.json` with the following contents, substituting the repositoryUri from the previous section for the image field, and env variable filler text for the real slack API token (same one with running the docker image locally):

```
{
  "family": "spiderfacts",
  "containerDefinitions": [
    {
      "name": "spiderfacts",
      "image": "aws_account_id.dkr.ecr.us-west-2.amazonaws.com/spiderfacts",
      "cpu": 1,
      "memory": 500,
      "essential": true,
      "environment": [
        {
          "name": "SPIDER_FACTS_TOKEN",
          "value": "xoxb-############-########################"
        }
      ]
    }
  ]
}
```

1.  `aws ecs register-task-definition --cli-input-json file://spiderfacts-task-def.json` => Register a task definition
1.  At this point, a cluster must be created before continuing. I created mine from the web interface because I wasn't sure how to do it from the AWS CLI.
1.  `aws ecs run-task --task-definition spiderfacts --cluster spiderfacts`

### Misc AWS/Docker notes

* Neither AWS nor Docker need port rules for the app to function.
* The Docker image will need to be rebuilt any time code changes. There is a way to mount a "code" volume the Docker image can share with one's dev machine. Combining that setup with a tool like nodemon will allow the developer to simply save the file to refresh the Docker image to the latest dev version.
* Automate the above with something like Concourse! CircleCI -> run tests, build Docker image, publish image to artifactory. Then use Concourse (aws CLI) or Terraform (modular config format, can resume from last errored state, publish to most cloud providers, best way) or Cloudformation (single file, has to restart entire deploy, publish only to AWS, still better than AWS CLI) to push image to AWS and everything else you need.
