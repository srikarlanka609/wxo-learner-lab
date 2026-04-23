## PART 0: Setting up the environment

First start by getting your IBM `IAM API Key` with the steps in the [Get IAM API Key](./get-iam-api-key.md) page.

Next start by navigating to the [IBM Cloud Dashboard](https://cloud.ibm.com/) and click on the `Hamburger` icon in the top left. 

![ibm-cloud-home](./assets/ibm-cloud-hamburger.png)

Click on the `Resource list` tab.

![ibm-cloud-navigate-to-resource-list](./assets/ibm-cloud-navigate-to-resource-list.png)

Now you should see a list of drop downs and be on the [https://cloud.ibm.com/resources](https://cloud.ibm.com/resources).

Click on the `AI / Machine Learning` drop down and then click on the `watsonx Orchestrate-nsrpoc` link.

![ibm-cloud-resource-list](./assets/cloud-resource-list.png)

> It should be titled: `watsonx Orchestrate-nsrpoc` but if you do not see that click on the one which has `watsonx Orchestrate` as the Product.

Now, you can click on the `Launch watsonx Orchestrate` button and proceed to the next phase.

![ibm-cloud-launch-orchestrate](./assets/cloud-wxo.png)

## PART I: Building a purchase agent to help users submit requests for new software
To kickoff the lab, we want to build an agent that can help us handle purchase requests. Imagine a user wants to purchase some new software but there are criteria we want to check on to reduce unneccessary approvals.  

In this section, we will build an agent that uses an agentic workflow tool and a 3rd party tool to help users fill out a form for a simple software request and submit a ServiceNow ticket request if criteria is met.  

> Your starting point should be [https://us-south.watson-orchestrate.cloud.ibm.com/chat](https://us-south.watson-orchestrate.cloud.ibm.com/chat), 

> You can navigate there following the steps in [Part 0](#part-0-setting-up-the-environment)

### Build our purchase_agent the UI  
Click on the `hamburger` icon in the top left.

![wxo-hamburger](./assets/part_one/wxo-hamburger.png)

Then `Build`

![wxo-build](./assets/part_one/wxo-build.png)

Then `Create agent +`

![wxo-agents-home](./assets/part_one/wxo-agents-home.png)

Select `Create from scratch`, and enter the following  
Name: 
```
purchase_agent
```  
Description: 
```
This agent will be used to help answer inquiries related to submitting a request for new purchase of software.
```  

Once you are done, hit `Create`

![wxo-create-first-agent](./assets/part_one/wxo-create-first-agent.png)

Next, click into `Behavior` and paste the following

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

![wxo-behavior-first-agent](./assets/part_one/wxo-behavior-first-agent.png)

### ServiceNow Agent setup
Now that we have our basic agent blueprint mapped out, we can begin by adding the additional tools and catalog agents we will need to use it successfully.

> For reference, only one user on the Instance needs to complete the following steps. Since we are sharing a workspace, we can all reference the tools and connections created by someone on this instance.

Go back to the `hamburger` icon in the top left. 

![wxo-agent-hamburger](./assets/part_one/wxo-agent-hamburger.png)

Click on `Build`

![wxo-agent-build](./assets/part_one/wxo-agent-build.png)

Click on `Create agent +`

![wxo-agents-home](./assets/part_one/wxo-agents-home.png)

Click on`Start with a template` tab.  

![wxo-create-from-template](./assets/part_one/wxo-create-from-template.png)

Follow the below steps to add in our ServiceNow agent that we can use in collaboration to help the management of tickets.

Search for `ServiceNow` in the search bar and scroll down to the `Ticket Manager Agent`. 

![wxo-catalog-search-servicenow](./assets/part_one/wxo-catalog-search-servicenow.png)

Click on the `Ticket Manager Agent` and then click on `Use as Template`.

![wxo-use-template-servicenow](./assets/part_one/wxo-use-template-servicenow.png)

> These agents are ready to use agents that can also serve as templates if you need specific functionality within your connections, apps etc. For the purpose of this lab, we will not be editing this agent at all, however depending on your use case you can edit every single detail within this agent.

Scroll down or click on `Toolset`. Click on the `three dots` next to the `Create a ticket in ServiceNow` tool and then `Edit details`.

![wxo-tools-edit-details-servicenow](./assets/part_one/wxo-tools-edit-details-servicenow.png)

Choose the `Connectors` option and click on the `Pencil` to edit.  

![wxo-tools-edit-connections](./assets/part_one/wxo-tools-edit-connection.png)  

Choose `Oauth2 Authorization Code`.

![wxo-tools-authentication-type](./assets/part_one/wxo-tools-authentication-type.png)

Fill out the following information and select on the `Team credentials` option.

Server URL: 
```
https://dev212075.service-now.com/
```  
Token URL: 
```
https://dev212075.service-now.com/oauth_token.do
```
Authorization URL: 
```
https://dev212075.service-now.com/oauth_auth.do
```  
Client ID: 
```
eb11f37583d44017b2a38a3b00595e5b
```  
CLient Secret: 
```
5v9Qg1Y(5k8rX.QcOPE0]5Rr.8N-AUC
```  

![wxo-tools-connections-filled](./assets/part_one/wxo-tools-connections-filled.png)

> **Notes**

> If you were creating the connection on the ServiceNow side, you would want to keep track of the `Callback URL` and probably add a `Scope`.

> `Team Credentials` is instance level while `Member Credentials` is user level and would need to authenticate when the tool call is made. 

> You can also `Paste draft configuration` in the `Live` or `Deployed` agent by re-opening the connection details by clicking on the pencil and selecting the `Live` option and re-authenticating. 

Once you filled out the information, click `Save` and `Authenticate`.

After the you try to connect, you have to login with the following creadentials and authorize:

`username`: 
```
admin
```  
`password`: 
```
GZ%*8cmWmdB3
```  
> **Notes**

> **Important**

> If you are viewing this after the lab and the above credentials are expired or not working, follow the steps in the [ServiceNow Setup](./servicenow-setup.md) to create a developer instance and create an application in ServiceNow.

> ServiceNow implemented a change to their developer portal recently and when you try to connect it says `Failed`, this is sometimes incorrect, test the connection by going to the `Ticket Manager Agent` and typing in the `Preview` window: "I'd like to create a ticket with Priority 1 and short description: this is a test ticket" and see if it returns a ticket number/is successful. If it does, then the connection is working. 

### Building our agentic workflow 

Click on the `hamburger` icon in the top left, then `Build`.

![wxo-agent-build](./assets/part_one/wxo-agent-build.png)

Then click into `All tools`, then click `Create tool +`.

![wxo-create-tool](./assets/part_one/wxo-create-tool.png)

Click on `Agentic workflow`.

![wxo-create-agentic-workflow](./assets/part_one/wxo-create-agentic-workflow.png)

Add `sw_validator_workflow` (along with your initials) as the Name and click `Start Building`. 

![wxo-name-agentic-flow](./assets/part_one/wxo-name-agentic-flow.png)

Now, we will be implementing a basic workflow where we ask a user the price and number of licenses needed.  

**Rules**:

If the price is less than 0 (not possible) or greater than or equal to 10000 (too expensive), we cannot continue.  

If we are able to meet the price condition, we will ask a second question about how many licenses are needed.  

If we need greater than 0 and less than or equal to 1000 licenses, we can successfully continue and be prompted with a ServiceNow ticket to complete regarding this request.  

#### **Step 1**. Let's begin our workflow by including a welcome message.

Click on the `Add +` button, then under User Actvities, hover over `Present to user` and select `Message`.

![wxo-flows-add-message](./assets/part_one/wxo-flows-add-message.png)

Now click on the the green `Message 1` box and click on the `Pencil` to rename the message box to `Welcome`. Paste the following in the output message: 

`Output message`: 
```
Welcome! Let's validate this request!
```  

![wxo-flows-setup-message](./assets/part_one/wxo-flows-setup-message.png)

> **Note**

> To save simply click out of what you are editing. 

#### **Step 2**. Now, click on the `+` sign between the `welcome` and `End` button. 

This time, we will begin with our first question so hover over `Collect from user` and click `Number` since we will be asking for price.

![wxo-flows-collect-number](./assets/part_one/wxo-flows-collect-number.png)

Click into the `Node` and on the `Pencil` icon and rename the name.

`name`:
```
What is the USD cost for this software?
```

![wxo-flows-setup-collecting-number](./assets/part_one/wxo-flows-setup-collecting-number.png)

> **Note**

> This is what is Displayed to the user: "What is the USD cost for this software?"

Here's what our workflow should look like right now.  

![wxo-flows-wxo-flows-checkin.png](./assets/part_one/wxo-flows-checkin.png)

#### **Step 3**. Now we are going to track the value of the user response in a variable using a logic block so we can use this later on. 

Similar to the steps above, click the `+` button under the `What is the USD cost for this software?` block. 
Hover over `Add a flow activity` and click `Logic block`.

![wxo-flows-logic-block](./assets/part_one/wxo-flows-logic-block.png)

You will then click on the `Logic block 1` and then `Open code editor` and can delete all of the pre-existing code.

Paste the following in the `code editor`:

`code`:
```
flow.private.cost = flow["User activity 1"]["What is the USD cost for this software?"].output.value
```

![wxo-flows-code-editor](./assets/part_one/wxo-flows-code-editor.png)

> To save you can either click out of the code editor screen or the `X` at the top right of the `code editor` window.

#### **Step 4**. Next, we will add a branch where we can actually evaluate the user input using our variable above.

Similar to the steps above, click the `+` button under the `Logic Block 1` block.  

Hover over `Add a flow control` and click `Branch`.

![wxo-flows-branch-1](./assets/part_one/wxo-flows-branch-1.png)

Click into the `Branch 1` object and under the `If` and `Else` Path conditions and click `Edit condition`.

Click the `+` sign next to `If` and click the question under `User activity 1`.

![wxo-flows-condition-1](./assets/part_one/wxo-flows-condition-1.png)

Now click the `+` next to `if` `123 value`, set the condition: `if 123 value >= 0`. 

Next, click outside and click `Add condition +`, repeat the above process but end with `and 123 value < 10000`.  

![wxo-flows-condition-2](./assets/part_one/wxo-flows-condition-2.png)

> Feel free to rename **Path 1** and **Path 2** in the Branch by first clicking on `Branch 1` and then `Path 1` and `Path 2` respectively. You can name them `Cost satisfied` and `Cost criteria not`.

You will now see 2 different paths, based on the outcome from the above.  

#### **Step 5**. 

Click on the green `Add +` button and follow the steps we used in **Step 1** to create another `Present to User` `Message`. 

![wxo-flows-message-2](./assets/part_one/wxo-flows-message-2.png)

This time, use output message should be:

`Output Message`:
```
Cost is invalid or too expensive! Criteria is not met.
```

and 

`title`:
```
Cost not met
```

Essentially, if the cost is too expensive or invalid, the user is presented this message and the flow ends. 

#### **Step 6**. We will now expand the Cost Satisfied Branch. This is the case where the price critiera was met so we can continue evaluating if this request is permissible. 

Click `+`, hover over `Collect from user` and click `Number` since we will be asking for number of licenses.

![wxo-flows-collect-number-2](./assets/part_one/wxo-flows-collect-number-2.png)

Follow the steps in step 2 but instead use rename the block to:

`Name`: 
```
How many licenses are needed?
```  

> This is the question that the user will see and be prompted to answer (with a Number).

![wxo-flows-checkin-2](./assets/part_one/wxo-flows-checkin-2.png)

#### **Step 7**. Now, we will similarly track the variable value like we did for cost, so follow the step 3

Click on the `+` under the `How many licenses are needed?` block and click `Add flow activity` and then `logic block`.

![wxo-flows-add-logic-block-2](./assets/part_one/wxo-flows-add-logic-block-2.png)

From here, you will have to click back into `Logic block 2` and then `Open code editor`.

You can also delete everything in the default code editor and just have the following:

`code`:
```
flow.private.num_licenses = flow["User activity 1"]["How many licenses are needed?"].output.value
```  

> To save, click on the `X` on the top right of the `Code editor` window.

#### **Step 8**. Now that we have a logic block, we will add another branch based on how many licenses are needed.  

We will set up the following two paths:

Criteria is met if we need 1-1000 licenses, otherwise, we cannot continue. 

Follow Step 4, but use value > 0 and value <= 1000 instead. Here's what your branch block should include.  

![wxo-flows-branch-2-final](./assets/part_one/wxo-flows-branch-2-final.png)

#### **Step 9**. We will follow Step 5, but instead create a criteria not met display message for our number of licenses question.

Follow Step 5 to create a `Present to User` `Message` if the Number of Licenses is criteria is not meant with

`title`: 
```
Licenses not met
``` 

and 

`Output message`: 

```
The number of licenses is either invalid or too many! Criteria is not met.
```  

![wxo-flows-criteria-not-met-2](./assets/part_one/wxo-flows-criteria-not-met-2.png)

#### **Step 10**. Let's add a display message under the path where the criteria for number of licenses was met. 

Follow steps 5/9 above for how we would build a `Present to User` `Message` using the 

`title`: 

```
Criteria met
``` 

and 

`Output message`: 

```
Criteria met! We will now fill out a ServiceNow Ticket.
``` 

![wxo-flows-criteria-met-message-2](./assets/part_one/wxo-flows-criteria-met-message-2.png)

#### **Step 11**. The last step in completing our workflow is now adding in our ServiceNow tool. 

Under the `Criteria met` `Display message` box, let's add a tool call. 

We can do this by click `+`, `Call a tool`, and search `Create a ticket in ServiceNow` and drag it into the correct space (Under `Criteria met`).

> You can select whichever `Create a ticket in ServiceNow` tool if they are several, they should all work the same for this purpose.


![wxo-flows-servicenow-tool](./assets/part_one/wxo-flows-servicenow-tool.png)

Click the `Done` button in the top right.

Here's what our final workflow should look like.  

![wxo-flows-final](./assets/part_one/wxo-flows-final.png)

Now to implement your workflow, navigate back to the `purchase_agent` you just made by clicking `All agents` and then `purchase_agent`.

![wxo-agents-home-2](./assets/part_one/wxo-agents-home-2.png)

Then scroll down or click on `Toolset` and `Add tool`.

![wxo-agents-add-tool](./assets/part_one/wxo-agents-add-tool.png)

Click on `Local Instance`.

![wxo-tools-local-instance](./assets/part_one/wxo-tools-local-instance.png)

Then search `sw_validator_workflow` and find the one you made and click `Add to Agent`.

![wxo-agents-add-flow](./assets/part_one/wxo-agents-add-flow.png)


Now you are complete! Test you agent in the `Preview` window by saying:

```
Hi
```

or 

```
Hello
```

> Continue the flow following remembering what answers Met the Criteria defined above. For the 6 question form, fill it out however you want noting that only Priority and Short Description are required. I normally put `Pririotiy 1` and `Short Description: "This is a test {date} - {initials}"`. This will then populate a record in the ServiceNow application you connected.

## PART II: Building a document agent analyst to handle all document inquiries

In this section, we will build an agent that will use documents as a knowledge base to answer relevant questions.

### watsonx Orchestrate ADK

As mentioned above, the ADK allows hosting the core Orchestrate components on a developer laptop. For the lab, you will run the ADK on your own laptop. 

To run it on your own laptop, you need to install:
- Python 3.11 +
> Note: Python 3.14 is currently not supported

For initial setup, we recommend the following steps, but if you want to use a different virtual environment manager or run into any issues please refer to the steps here: [the ADK install page](https://developer.watson-orchestrate.ibm.com/getting_started/installing)

These steps will help install the ADK, add & activate your environment to begin building! 

##### Mac Setup
###### Step 1: Install homebrew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
###### Step 2: Install uv with either:
```
brew install uv
```
or directly with a curl command:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
###### Step 3: Set up uv venv:
```
uv venv --python 3.11
source .venv/bin/activate
```

Go to the [Install the ADK](#install-the-adk) section to continue.

##### Windows Setup
###### Step 1: Install uv
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex
```
###### Step 2: Set up uv venv
```
uv venv --python 3.11
.venv\Scripts\activate
```

#### Install and set up the ADK
```
uv pip install ibm-watsonx-orchestrate
```

Now you will set up an environment for the ADK. This will allow you to create and manage agents, and to run them. 

First in an orchestrate window, click on your `name` in the top right and then `settings`.

![wxo-settings](./assets/part_two/wxo-settings.png)

Then copy and save the `Service Instance URL` and if you haven't created an `API Key` click `Generate API Key` and copy amd save that as well. 

![wxo-api-details](./assets/part_two/wxo-api-details.png)


Now run the command to create your environment with:

```
orchestrate env add -n <your_env_name> -u <your_service_instance_url>
```

or

```
uv run orchestrate env add -n <your_env_name> -u <your_service_instance_url>
```

Now you can finally activate your environment with the following commands (you will have to paste your API key to activate):

```
orchestrate env activate <your_env_name>
```

or

```
uv run orchestrate env activate <your_env_name>
```

> Note when pasting your API Key to activate your environment, you will not see what you paste, but it will be there. 

Once you're virtual environment is activated, you can confirm this by entering

```bash
orchestrate agents list
```

You should see a couple of agents from our previous lab portion, namely the ServiceNow `Ticket Manager Agent` and the `purchase_agent`.  


Navigate to your repository that you cloned this repo in, and to the  `~/wx-orchestrate/agents` directory. you should see a YAML file called `document_agent.yaml`
This file is the blueprint for our agent and we will use the ADK to import this into our environment. 

![image](./assets/21.png)


Run the following command to import this agent into the environment: 
```bash
orchestrate agents import -f document_agent.yaml
```
You should see the following message

![image](./assets/22.png)


### Modify agent in the UI
Go back into your orchestrate instance, refresh and your `document_agent` should be there. Click into it, and scroll down to the `Knowledge` portion. Click `Add source +`, then `New knowledge`, `Upload files`, and attach the five provided documents that you have downloaded. 

Each of these are different contractual agreements between a vendor and client, laying out all expectations requirements, and agreed-upon goals. Each of these five files have different formatting, structure, and amount of information that represents inherent differences in contract structure. 

Insert the following prompts one-by-one and see how we can answer questions about our five documents.

#### Prompt 1. 
```
Does CloudTech Solutions Inc retain any right in having Global Manufacturing Corporation's data outside of providing required services?
```
#### Prompt 2. 
```
Within how many days should the licensor DataVault deliver the software to the licensee Regional Health Care and it what forms can it be delivered?
```  
#### Prompt 3
```
If I am requesting additional services in the managed services agreement, how much will 3 senior engineers and 1 technician for 8 hours cost on a standard non-holiday weekday?
```  
#### Prompt 4
```
Tell me the risk management strategy outlined for the on-prem to AWS migration.
```
#### Prompt 5
```
From the Enterprise Solutions Group vendor point of view, if the customer ask for support on their McAfee security software, is it okay for us to put resources towards this?
```  
#### Prompt 6
```
Compare and contrast the payment structures across all five contracts. Which agreement has the least risk in exceeding a total cost of $2 million?
```
#### Prompt 7
```
Give me a list of all assets/supported technologies in the software maintenance and perpetual license agreements.
```

### Enhancing our agent with an MCP tool
Currently, our agent is able to answer questions pertaining to each of the five documents and perform some analysis like we've just done so far. While our agent is functional, it is currently limited to our five documents.  

A user may be interested in industry-wide standards, pricing, compliance, or information that can be relevant in analyzing these documents.  
We can broaden our agent and give it the capability for searching the web through an `MCP Server`

An `MCP Server` is a lightweight program following MCP, an open-protocol created by Anthropic to standardize how AI agents can connect to external data sources and tools. Think of it as an USB flash drive for an AI assistant where different MCP servers contain access to different resources and we can use a flash drive to get access to such resources.

We are going to setup an MCP server and specifically using a searchweb tool so our agent can browse the internet when relevant.  

Scroll to the `Toolset` section and click `Add tool +`.  

![image](./assets/23.png)

![image](./assets/24.png)

![image](./assets/25.png)

Insert the following:

**Server Name**: 
```
websearch_mcp
```  
**Install Command**: 
```bash
npx -y @guhcostan/web-search-mcp
```  

Once you add the MCP server you should see a tool for `websearch_mcp:search_web`. Select and click on it to add it to the agent. 

Before we begin using it, let's make sure our agent instructions contain behavior for when we need to use this tool. Go to the `Behavior` section and add the following to the instructions:  

```
If a user asks about any of the vendors, clients or project topics that span beyond just the documents such as industry-wide standards, compliance, financial analysis, and competitive analysis, use the `websearch_mcp:search_web` tool to fulfill the request. 
```

Now, we can refresh and should be able to begin asking questions. Insert the following prompts one-by-one and see how we can use our tool.

#### Prompt 1
```
Give me some reviews on CloudFirst Consulting Partners Inc?
```

#### Prompt 2
```
Can you tell me the Oracle database licensing cost per core?
```

#### Prompt 3
```
What is considered industry-wide network latency acceptable thresholds in cloud computing?
```

Great! Now, we have been able to enhance our agent and use it to not just analyze documents, but also help users ask useful, relevant questions in analyzing vendor contracts. 




## PART III: Building A User Agent to confirm credit card requirements

In this section, we will build a user agent that can confirm if the user has a credit card on file and if the credit card is active and can be used by systems. We will use a plug-in guardrail to ensure at no point the entire credit card number is leaked to the agent.

### Orchestrate Plugins
Watson Orchestrate plug-ins play a role in enhancing the capabilities and robustness of agents. They help enable custom behavior to be easily added to an agent’s processing flow, allowing modifications to incoming input or outgoing output. This customization is essential for applications where agents must comply with safety, security, and regulatory requirements. Plug-ins protect the agent from problematic inputs by filtering or sanitizing content and enforce compliance by applying guardrails to sensitive or restricted information. 
> For this lab we would be tackling pre and post invoke issue with sensitive information like credit card numbers. 
> Also, for this section of the lab we would be be using the ADK to deploy everything and then verify the agent on the Watson Orchestrate UI.

#### Import Credit Card Check Plugin
```bash
orchestrate tools import -k python -f credit_card_masking_plugin.py
```

- This plugin will mask the credit card number in the agent response and user query and also mention the safety measure by prompting the user to not share the credit card number.Got through the credit_card_masking_plugin.py to understand how the masking function is used for ensuring secure messages.

#### Import User Tools
```bash
orchestrate tools import -k python -f customer_query_tool_package/customer_query_tool.py -p customer_query_tool_package
```

- This tool file will help the agent interact with an sqlite database to check if the user has a credit card on file and if the credit card is active and can be used by systems. This will upload three tools 
    - `get_customer_info` - Query customer by ID or name
    - `list_all_customers` - List all customers in database
    - `get_customer_credit_card` - Get credit card info for a customer

- When tools are deployed to Watson Orchestrate, they run in isolated containerized environments. Hence we can deploy all the dependencies in the tools folder and add the package to the tool deployment on the ADK (the approach we used here to ensure the db is accessible to the tool) If you have specific package requirements, you would also add the requirements.txt to this folder - customer_query_tool_package


#### Verify tools imports
```bash
orchestrate tools list
```

#### Create agent
```bash
orchestrate agents create -f user_agent.yaml
```

- This will create a user agent that can confirm if the user has a credit card on file and if the credit card is active and can be used by systems. Some sample prompts:

#### Prompt 1
```
Do I have an active credit card on file? My Name is Vaisakhi Mishra
```

#### Prompt 2
```
Do I have an active credit card on file? My Name is John Smith
```

#### Prompt 3
```
Is my credit card 3782-3456-7890-1234 still active?
```

#### Prompt 4
```
Is my credit card 4532-1234-5678-9010 on file?
```

#### Prompt 5
```
When does my credit card 4532123456789010 expire?
```
  

#### Verify deployment
```bash
orchestrate agents list
```

## PART IV: Connecting to Different Interfaces and LLMs
While we have built powerful agents in the UI and via the ADK, agents are most effective when they live where your users are.
In this final section, we will bridge the gap between platforms by connecting our agents to Slack for real-time chat and swapping the underlying "brain" of our agent to use an OpenAI LLM.

### Connecting to Slack
This bridge allows your agent to participate in conversations and respond to user queries directly within your workspace. Allowing your agent to meet potential users where they do work with a few steps.
> more resources on this setup here: https://www.ibm.com/docs/en/watsonx/watson-orchestrate/base?topic=channels-connecting-slack

First, navigate to the agent you want to use in Slack and click on `Channels` on the left-hand side. Select `Slack`, set the environment to `Draft`, and click `Create New`.
  ![alt text](./assets/connect_slack/create-slack.png)

Next, follow the steps provided in the UI to configure the Slack Interface. 
> Once done, you will have to navigate to that workspace in slack and then @ the bot's name, it should be able to answer your questions after joining the channel.

### Connecting to OpenAI LLMs
Now you can add external models to watsonx Orchestrate to support any existing providers (including both large and small models). To do so, use a model.yaml file and the commands below: 
> more resources here: https://developer.watson-orchestrate.ibm.com/llm/managing_llm

Initialize your environment and set up the secure credential store
```bash
orchestrate connections add -a openai_credentials
orchestrate connections configure -a openai_credentials --env draft -k key_value -t team
orchestrate connections set-credentials -a openai_credentials --env draft -e "api_key="
```

Import the model specification to the AI Gateway
```bash
orchestrate models import --file ./models/gpt-model.yaml --app-id openai_credentials
```

Now you can view the models in watsonx Orchestrate with:
```bash
orchestrate models list
```
> imported models start with `virtual-model`

Once the model is imported, you will update your agent's configuration to use this new LLM. This allows you to control whether you are using large reasoning models or small, faster models. Allowing you to fit the right model for your specific use case.

Feel free to test this out, a sample agent yaml would be [here](./wx-orchestrate/agents/sample-openai-agent.yaml), all you would need to do is update the yaml file you want to test with to point towards the udpated model and re-import the agent.
