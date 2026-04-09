



## PART II: Building a document agent analyst to handle all document inquiries
Suppose, you have different vendor documents and need ...
In this section, we will build an agent that will use documents as a knowledge base to answer relevant questions...


### watsonx Orchestrate ADK

As mentioned above, the ADK allows hosting the core Orchestrate components on a developer laptop. For the lab, you will run the ADK on your own laptop. 

#### Local machine

To run it on your own laptop, you need to install:
- Python 3.11 + 

For initial setup, we recommend the following steps, but if you want to use a different virtual environment manager please refer to the steps here: [the ADK install page](https://developer.watson-orchestrate.ibm.com/getting_started/installing)
These steps will help install the ADK, add & activate your environment, and begin building! 


Once you're environment is activated, you can confirm this by entering

`orchestrate agents list`

... something about you should see some agents from earlier part ...


Navigate to your repository and to the  **~/wx-orchestrate/agents** directory. you should see a YAML file called `document_agent.yaml`
This file is the blueprint for our agent and we will use the ADK to import this into our environment. 


Run the following command to import this agent into the environment: `orchestrate agents import -f document_agent.yaml`
![image](https://github.ibm.com/user-attachments/assets/82a6fd4e-79ae-454d-bfa7-bf99f08017cf)
