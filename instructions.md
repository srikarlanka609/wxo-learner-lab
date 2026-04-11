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

Now try a completely irrelevant prompt: `What is the capital of France?`  
you should see that we get a return message `This is out of scope.`
If you scroll to the Behavior, you should see a Guideline set in place, which is a rule we have to make sure our agent is focusing on just document-related inquiries. 

### Enhancing our agent with an MCP tool
Currently, our agent is able to answer questions pertaining to each of the five documents and perform some analysis like we've just done so far. While our agent is functional, it is currently limited to our five documents.  

A user may be interested in industry-wide standards, pricing, compliance, or information that can be relevant in analyzing these documents.  
We can broaden our agent and give it the capability for searching the web through an **MCP Server**

An **MCP Server** is a lightweight program following MCP, an open-protocol created by Anthropic to standardize how AI agents can connect to external data sources and tools. Think of it as an USB flash drive for an AI assistant where different MCP servers contain access to different resources and we can use a flash drive to get access to such resources.

We are going to setup an MCP server and specifically using a searchweb tool so our agent can browse the internet when relevant.  

Scroll to the **Toolset** section and click **Add tool +**.  

![image](https://github.ibm.com/user-attachments/assets/1b998715-0de0-41c0-84fd-a279e21b5b78)

![image](https://github.ibm.com/user-attachments/assets/fcd3fafa-8cb9-476b-bca5-15a03af85d1a)

![image](https://github.ibm.com/user-attachments/assets/ac32ca9c-46f7-47ec-b5d4-011ed88bde63)

Insert the following:  
**Server Name**: `websearch_mcp`  
**Install Command**: `npx -y @guhcostan/web-search-mcp`  

Once you add the MCP server you should see a tool for **websearch_mcp:search_web**. Select and click on it to add it to the agent. 

Before we begin using it, let's make sure our agent instructions contain behavior for when we need to use this tool. Go to the **Behavior** section and add the following to the instructions:  

- If a user asks about any of the vendors, clients or project topics that span beyond just the documents such as industry-wide standards, compliance, financial analysis, and competitive analysis, use the `websearch_mcp:search_web` tool to fulfill the request. 

Now, we can refresh and should be able to begin asking questions. Insert the following prompts one-by-one and see how we can use our tool.

1. `Give me some reviews on CloudFirst Consulting Partners Inc?`
2. `Can you tell me the Oracle database licensing cost per core?`
3. `What is considered industry-wide network latency acceptable thresholds in cloud computing?`

Great! Now, we have been able to enhance our agent and use it to not just analyze documents, but also help users ask useful, relevant questions in analyzing vendor contracts. 





