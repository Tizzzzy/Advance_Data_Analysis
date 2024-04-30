# Advance Data Analysis

This project leverages the `GPT Assistant API` and its `Code Interpreter Tool` to conduct sophisticated data analysis. Users can upload tabular data in various formats along with a prompt question. Our system processes this input to deliver tailored data analysis results, directly responding to the specified question.

## Demo

```
User: python code_interpreter.py
Assistant: Enter the file path or 'exit' to quit:
User: <file path>
Assistant: Enter your query or 'exit' to quit:
User: <your question query>
Assistant: RUNNING...

Assistant: <Answer in Text>
Assistant: <Answer in Image>

Assistant: Do you want to continue with the existing chat? (yes/no):
User: <yes/no>
Assistant: Do you want to use the existing file? (yes/no):
User: <yes/no>
...
```

## Get Start It

### Prerequisite:

```
# make sure your openai version >= 1.3.5
pip install --upgrade openai
```

### Things to Change:

1. Add your `Openai API Key`
   - You can find your API key [here](https://platform.openai.com/api-keys)
2. Change your `system prompt` (Optional)
   - Right now the predifined system prompt is a good start, but you can always change it to focus on your specific task
   - Notice the size of system prompt is limited to 512 char
3. Add your `user name` (Optional)
   - You can add it to better assist you
4. Change the model (Optional)
   - Right now the code is using the `gpt-4-1106-preview` model, you can explore other model as well.

If you like this project, please give me a star!
