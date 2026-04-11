## PART I: Building a purchase agent to help users submit requests for new software
.... some info ....
In this section, we will build an agent that uses an agentic workflow tool and a 3rd party tool to help users fill out a form for a simple software request and submit a ServiceNow ticket request if criteria is met.




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

![image](https://github.ibm.com/user-attachments/assets/2e660d5b-bb8f-44f3-9233-5c918f7ff32a)


Run the following command to import this agent into the environment: `orchestrate agents import -f document_agent.yaml`
You should see the following message
![image](https://github.ibm.com/user-attachments/assets/ee9094f4-3d09-45f9-b3eb-c4aa3bdd13d2)


### Modify agent in the UI
Go back into your orchestrate instance, refresh and your **document_agent** should be there. Click into it, and scroll down to the **Knowledge** portion. Click **Add source +**, then **New knowledge**, **Upload files**, and attach the five provided documents that you have downloaded. 

Each of these are different contractual agreements between a vendor and client, laying out all expectations requirements, and agreed-upon goals. Each of these five files have different formatting, structure, and amount of information that represents inherent differences in contract structure. 

Insert the following prompts one-by-one and see how we can answer questions about our five documents.

1. `Does CloudTech Solutions Inc retain any right in having Global Manufacturing Corporation's data outside of providing required services?`
2. `Within how many days should the licensor DataVault deliver the software to the licensee Regional Health Care and it what forms can it be delivered?`  
3. `For the agreed upon management of servers, if the average server CPU utilization is 75%, is this permissible?`  
4. `Tell me the risk management strategy outlined for the on-prem to AWS migration.`
5. `From the Enterprise Solutions Group vendor point of view, if the customer ask for support on their McAfee security software, is it okay for us to put resources towards this?`  

6. `Compare and contrast the payment structures across all five contracts. Which agreement has the least risk in exceeding a total cost of $2 million?`
7. `Give me a list of all assets/supported technologies in the software maintenance and perpetual license agreements.`


