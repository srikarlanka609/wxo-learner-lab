



## PART II: Using agents for RAG usecases
Suppose, you have different vendor documents and need ...
In this section, we will build an agent that will use documents as a knowledge base to answer relevant questions...


### watsonx Orchestrate ADK

As mentioned above, the ADK allows hosting the core Orchestrate components on a developer laptop. For the lab, you can choose if you want to run the ADK on your own laptop or on a virtual machine that will be provided to you by your instructor. 

#### Local machine

To run it on your own laptop, you need to install:
- Python 3.11 + 

For initial setup, we recommend the following steps, but if you want to use a different virtual environment manager please refer to the steps here: [the ADK install page](https://developer.watson-orchestrate.ibm.com/getting_started/installing)

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


> If you'd like to to update your python version, or have different configurations, follow the steps [here](https://developer.watson-orchestrate.ibm.com/getting_started/installing) until you install the ibm-watsonx-orchestrate package.

Then run the following to install the ADK:
```
pip install --upgrade ibm-watsonx-orchestrate
```

If you have any issues, these instructions go more into detail: [the ADK install page](https://developer.watson-orchestrate.ibm.com/getting_started/installing)





