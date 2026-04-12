## PART I: Building a purchase agent to help users submit requests for new software
To kickoff the lab, we want to build an agent that can help us handle purchase requests. Imagine a user wants to purchase some new software but there are criteria we want to check on to reduce unneccessary approvals.  
In this section, we will build an agent that uses an agentic workflow tool and a 3rd party tool to help users fill out a form for a simple software request and submit a ServiceNow ticket request if criteria is met.  

### Build our purchase_agent the UI  
Click on the **hamburger** icon in the top left, then **Build**, then **Create agent +**, then **Create from scratch**, and enter the following  
Name: `purchase_agent`  
Description: `This agent will be used to help answer inquiries related to submitting a request for new purchase of software.`  
Once you are done, click into **Behavior** and paste the following

```
==========================================================
  SYSTEM PROMPT — SOFTWARE PURCHASE VALIDATOR
  ==========================================================
  GREETING BEHAVIOUR
  - If the user says “hi” or “hello”, respond with:
    "Hello, I am here to help you validate your software request." 

  GLOBAL RULES (STRICT)
  - Always acknowledge the user politely
  - Ask ONE question at a time
  - Always use American English

STEP 1: invoke the `sw_validator_workflow`
STEP 2: upon completion, return to user "Complete!"
```  

### ServiceNow Agent setup
Now that we have our basic agent blueprint mapped out, we can begin by adding the additional tools and catalog agents we will need to use it successfully.
Go back to the **hamburger** icon in the top left, then **Build**, then **Create agent +**, then **Start with a template** tab.  


Follow the below steps to add in our ServiceNow agent that we can use in collaboration to help the management of tickets

![image](https://github.ibm.com/user-attachments/assets/e50bac71-35ca-451f-886f-477480d25212)
Search for ServiceNow in the search bar and scroll down to the Ticket Manager Agent  
![image](https://github.ibm.com/user-attachments/assets/ee2fa2e8-1ad6-439e-b363-a7c0910fa70f)

![image](https://github.ibm.com/user-attachments/assets/a1a1f476-7a12-4955-8895-7a8085a0f165)  

Click on the Ticket Manager Agent and then click on Use as Template. These agents are ready to use agents that can also serve as templates if you need specific functionality within your connections, apps etc. For the purpose of this lab, we will not be editing this agent at all, however depending on your use case you can edit every single detail within this agent.

![image](https://github.ibm.com/user-attachments/assets/31f0b422-55b3-40b3-9b88-f38d5bb5ca27)

Scroll down to Toolset. Click on the three dots next to the **Create a ticket in ServiceNow** tool and then Edit details
![image](https://github.ibm.com/user-attachments/assets/e15402a8-a92e-45f9-ae79-9f9dccc4f0e1)  

Choose the **Connectors** option and click on the pencil to edit.  
![image](https://github.ibm.com/user-attachments/assets/cf2a63cf-2b8a-47de-8e9d-01f70064a428)  

Choose **Oauth2 Authorization Code**
![image](https://github.ibm.com/user-attachments/assets/c552f52a-6e7c-456c-8fc1-86c74739de3e)
Fill out the following information and select on the **Team credentials** option, then click Save changes  

Server URL: `https://dev281392.service-now.com/`  
Token URL: `https://dev281392.service-now.com/oauth_token.do`
Authorization URL: `https://dev281392.service-now.com/oauth_auth.do`  
Client ID: `6150dca3213d4941957b1c89c83ee49b`  
CLient Secret: `ZIB+ALl19Jvg1P@w!8,#G72Z[(WRRTQn`  


Once you saved them, re-open the connection details by clicking on the pencil. From here, select the Live option and click Paste draft configuration.  
Make sure **Team credentials** is selected for the Credential Type.  





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





